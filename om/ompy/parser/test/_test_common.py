from pathlib import Path

FILE_LOC = Path(__file__).resolve().parent
TESTS_DIR = FILE_LOC / 'programs'
STATIC_DIR = TESTS_DIR / 'static'
NORM_DIR = TESTS_DIR / 'normalized'
ILLFORMED_DIR = TESTS_DIR / 'illformed'
OM_SCHEMA_FILE = FILE_LOC / '..' / '..' / '..' / 'om.schema.json'
