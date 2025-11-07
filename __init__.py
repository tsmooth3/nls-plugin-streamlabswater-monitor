"""
The **Stream Labs Water Monitor Board**
displays current water usage details along with historical average and max.
"""
import json
from pathlib import Path

#import values from plugin.json
plugin_json_path = Path(__file__).parent / "plugin.json"
with open(plugin_json_path, "r", encoding="utf-8") as f:
    _metadata = json.load(f)

# Expose metadata as module variables (backward compatibility)
__plugin_id__ = _metadata["name"]
__version__ = _metadata["version"]
__description__ = _metadata["description"]
__board_name__ = _metadata["description"]
__author__ = _metadata["author"]
__requirements__ = _metadata.get("requirements", []).get("dependencies", [])