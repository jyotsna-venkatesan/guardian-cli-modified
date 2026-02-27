"""
WhatWeb tool wrapper for web technology fingerprinting
"""

import json
from typing import Dict, Any, List

from tools.base_tool import BaseTool


class WhatWebTool(BaseTool):
    """WhatWeb technology fingerprinting wrapper"""
    
    def __init__(self, config):
        super().__init__(config)
        self.tool_name = "whatweb"
    
    def get_command(self, target: str, **kwargs) -> List[str]:
        """Build whatweb command"""
        # Get config defaults
        config = self.config.get("tools", {}).get("whatweb", {})

        # Use a temp file for JSON output to avoid IOErrors with stdout
        self._output_file = "/tmp/whatweb.json"

        command = ["whatweb"]
        command.extend(["--log-json", self._output_file])

        # Aggression level (1-4) - workflow parameter or config or default
        aggression = kwargs.get("aggression", config.get("aggression", 1))
        command.extend(["-a", str(aggression)])

        # Follow redirects - workflow parameter or config or default
        if kwargs.get("follow_redirects", config.get("follow_redirects", True)):
            command.append("--follow-redirect=always")

        # User agent - workflow parameter or config or default
        user_agent = kwargs.get("user_agent", config.get("user_agent", "Guardian-Pentest-Tool"))
        command.extend(["--user-agent", user_agent])

        # Target
        command.append(target)

        return command
    
    def parse_output(self, output: str) -> Dict[str, Any]:
        """Parse whatweb JSON output from temp file"""
        results = {
            "technologies": [],
            "web_server": None,
            "programming_languages": [],
            "cms": None,
            "javascript_frameworks": [],
            "http_status": None,
            "plugins": []
        }

        # Read from the temp file created by whatweb
        try:
            with open(getattr(self, '_output_file', '/tmp/whatweb.json'), 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception:
            lines = output.strip().split('\n')  # fallback to output if file missing

        for line in lines:
            if not line:
                continue
            try:
                data = json.loads(line)

                # HTTP status
                if "http_status" in data:
                    results["http_status"] = data["http_status"]

                # Extract plugins (technologies)
                plugins = data.get("plugins", {})

                for plugin_name, plugin_data in plugins.items():
                    tech = {
                        "name": plugin_name,
                        "version": None,
                        "categories": []
                    }

                    # Extract version if available
                    if isinstance(plugin_data, dict):
                        version = plugin_data.get("version")
                        if version:
                            tech["version"] = version[0] if isinstance(version, list) else version

                    results["plugins"].append(tech)

                    # Categorize common technologies
                    plugin_lower = plugin_name.lower()

                    if plugin_name in ["Apache", "nginx", "IIS", "LiteSpeed"]:
                        results["web_server"] = tech
                    elif plugin_name in ["PHP", "Python", "Ruby", "ASP.NET"]:
                        results["programming_languages"].append(plugin_name)
                    elif plugin_name in ["WordPress", "Joomla", "Drupal"]:
                        results["cms"] = tech
                    elif plugin_name in ["jQuery", "React", "Vue", "Angular"]:
                        results["javascript_frameworks"].append(plugin_name)

                    results["technologies"].append(plugin_name)
            except json.JSONDecodeError:
                continue

        return results
