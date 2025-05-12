"""
[augmented urban data triangulation (audt)]
[audt-data]
[Batch Pp]
[Module with functions for batch pp]
[Matt Franchi]
"""

import os
import json
import pandas as pd
import glob
import re
import subprocess
import sys
from pathlib import Path
from audt_data.d03_src.utils.logger import setup_logger
from audt_data.d03_src.utils.repo import get_repo_root
from audt_data.d03_src.pp.acs.helpers import parse_md, parse_acs
# Set up the logger
logger = setup_logger("acs.batch_processor")

def extract_acs_metadata(filename):
    """
    Extract metadata from ACS filename (year, identifier).
    
    Expected format: acs{year}_{identifier}.json
    """
    basename = os.path.basename(filename)
    match = re.match(r'acs(\d{4})_(.+)\.json', basename)
    if match:
        year, identifier = match.groups()
        return int(year), identifier
    else:
        logger.error(f"Could not parse filename: {basename}")
        return None, None

def process_acs_file(input_file, output_dir):
    """Process a single ACS dataset file"""
    try:
        year, identifier = extract_acs_metadata(input_file)
        if not year or not identifier:
            return False
        
        logger.info(f"Processing ACS {year} - {identifier}")
        
        # Check if file exists and has content
        if not os.path.exists(input_file) or os.path.getsize(input_file) == 0:
            logger.error(f"File {input_file} is empty or does not exist")
            return False
        
        # Try to load the raw data with proper error handling
        try:
            with open(input_file, 'r') as f:
                content = f.read().strip()
                
                # Check if file is empty or just whitespace
                if not content:
                    logger.error(f"File {input_file} is empty")
                    return False
                    
                # Try to parse JSON
                data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from {input_file}: {e}")
            
            # Try alternative parsing methods
            try:
                # Some files might be CSV or other format - check first few bytes
                with open(input_file, 'rb') as f:
                    header = f.read(4)
                    
                if header.startswith(b'PK'):
                    logger.error(f"File {input_file} appears to be a ZIP file")
                elif content and (content[0] == '<' or content.startswith('<?xml')):
                    logger.error(f"File {input_file} appears to be an XML file")
                else:
                    # Try as CSV
                    try:
                        df = pd.read_csv(input_file)
                        logger.info(f"Successfully parsed {input_file} as CSV")
                        # Process CSV data differently
                        # ...
                    except Exception:
                        logger.error(f"Could not parse {input_file} as CSV either")
            except Exception as alt_err:
                logger.error(f"Alternative parsing failed for {input_file}: {alt_err}")
                
            return False
        
        # Parse metadata to get column mapping
        if 'variables' in data:
            # This is a metadata file
            logger.info(f"Processing metadata file: {input_file}")
            try:
                metadata = parse_md(data)
                
                # Save processed metadata
                output_path = os.path.join(output_dir, f"acs{year}_{identifier}_metadata.csv")
                metadata.to_csv(output_path)
                logger.success(f"Saved processed metadata to {output_path}")
            except Exception as e:
                logger.error(f"Error parsing metadata: {str(e)}")
                return False
        else:
            # This is a data file - we need column mapping
            # Look for metadata file with different naming patterns
            metadata_file = None
            
            # Try with _md.json suffix (seen in the error logs)
            md_file = os.path.join(os.path.dirname(input_file), f"acs{year}_{identifier}_md.json")
            if os.path.exists(md_file):
                metadata_file = md_file
            
            # Try with _metadata.json suffix (as in your original code)
            if not metadata_file:
                meta_files = glob.glob(os.path.join(os.path.dirname(input_file), 
                                                f"acs{year}_{identifier}_metadata.json"))
                if meta_files:
                    metadata_file = meta_files[0]
            
            if not metadata_file:
                logger.error(f"Could not find metadata file for {input_file}")
                return False
            
            try:    
                with open(metadata_file, 'r') as f:
                    metadata_data = json.load(f)
                
                metadata = parse_md(metadata_data)
                
                # Create column mapping
                col_mapping = {col: f"{col}_{desc}" for col, desc in 
                              zip(metadata['column'], metadata['desc_2'])}
                
                # Parse ACS data
                df = pd.read_json(input_file)
                
                # Remove data type conversion here - we'll handle it better in parse_acs
                # The improved parse_acs will handle data types appropriately
                
                # Process the data with the column mapping
                try:
                    parsed_data = parse_acs(df, col_mapping)
                    
                    # Add year column
                    parsed_data.loc[:, 'year'] = year
                    
                    # Save processed data
                    output_path = os.path.join(output_dir, f"acs{year}_{identifier}_processed.csv")
                    parsed_data.to_csv(output_path)
                    
                    # Log data type information for debugging
                    dtypes_msg = "Data types in processed file:\n" + "\n".join([f"{col}: {dtype}" for col, dtype in parsed_data.dtypes.items()])
                    logger.debug(dtypes_msg)
                    
                    logger.success(f"Saved processed data to {output_path}")
                except Exception as e:
                    # Log detailed error information
                    logger.error(f"Error processing data file: {str(e)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return False
            except Exception as e:
                logger.error(f"Error processing data file: {str(e)}")
                return False
                
        return True
    
    except Exception as e:
        logger.error(f"Error processing {input_file}: {str(e)}")
        return False

def batch_process_acs():
    """
    Batch process all ACS datasets in the repository and save processed data.
    
    Uses the standardized repository structure:
    - Raw ACS data is stored in {repo_root}/d01_data/acs/
    - Processed data will be saved to {repo_root}/d01_data/acs/preprocessed/
    """
    # Define directories using repository root
    repo_root = get_repo_root()
    if not repo_root:
        logger.error("Could not determine repository root. Aborting.")
        return
    
    # Update paths to match repository structure
    raw_dir = Path(repo_root) / "audt_data" / "d01_data" / "acs" / "raw"
    # go up a dir and go to preprocessed 
    preprocessed_dir = Path(raw_dir).parent / "preprocessed"
    
    # Create preprocessed directory if it doesn't exist
    os.makedirs(preprocessed_dir, exist_ok=True)
    
    # Find all ACS JSON files in raw directory
    files = glob.glob(str(raw_dir / "acs*.json"))
    
    if not files:
        logger.warning(f"No ACS files found in {raw_dir}")
        return
    
    logger.info(f"Found {len(files)} ACS files to process")
    
    # Process each file
    success_count = 0
    for file in files:
        if process_acs_file(file, preprocessed_dir):
            success_count += 1
    
    # Final report
    logger.info(f"Batch processing complete: {success_count}/{len(files)} files processed successfully")
    if success_count == len(files):
        logger.success("All files processed successfully!")
    else:
        logger.warning(f"Failed to process {len(files) - success_count} files")

if __name__ == "__main__":
    logger.info("Starting ACS batch processing")
    batch_process_acs()
    logger.info("Batch processing completed")
