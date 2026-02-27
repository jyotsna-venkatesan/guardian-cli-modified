from typing import List, Dict, Any
from tools.base_tool import BaseTool
import json
import re

class XSStrikeTool(BaseTool):
    """Wrapper for XSStrike - Advanced XSS Detection Suite"""
    
    def get_command(self, target: str, **kwargs) -> List[str]:
        # Ensure the target URL contains a parameter, as required by XSStrike
        import urllib.parse
        parsed = urllib.parse.urlparse(target)
        if not parsed.query:
            # Add a dummy parameter if none exists
            if '?' in target:
                target = target + '&test=1'
            else:
                target = target + '?test=1'

        cmd = ["xsstrike", "-u", target]

        if kwargs.get("crawl", False):
            cmd.append("--crawl")

        if kwargs.get("level"):
            cmd.extend(["-l", str(kwargs["level"])])

        if kwargs.get("headers"):
            cmd.extend(["--headers", kwargs["headers"]])

        # JSON output support in XSStrike is limited/experimental in some versions
        # We'll rely on parsing stdout or --json if available in the specific installed version
        # For this wrapper, we'll try to use --json if supported, otherwise parse stdout
        if kwargs.get("json_output", True):
            cmd.append("--json")

        # Add timeout
        if kwargs.get("timeout"):
            cmd.extend(["--timeout", str(kwargs["timeout"])])

        return cmd
    
    def parse_output(self, output: str) -> Dict[str, Any]:
        result = {
            "vulnerabilities": [],
            "crawled_urls": [],
            "raw_output": output
        }
        
        # Try to parse JSON lines if mixed in output
        for line in output.splitlines():
            try:
                if line.strip().startswith("{") and "vulnerable" in line:
                    data = json.loads(line)
                    if data.get("vulnerable"):
                        result["vulnerabilities"].append({
                            "url": data.get("url"),
                            "param": data.get("param"),
                            "vector": data.get("vector"),
                            "payload": data.get("payload")
                        })
            except json.JSONDecodeError:
                pass
                
        # Fallback: Regex parsing for standard output
        if not result["vulnerabilities"]:
            # Pattern for payloads found
            payloads = re.findall(r"Payload: (.*)", output)
            vectors = re.findall(r"Vector: (.*)", output)
            
            for i, payload in enumerate(payloads):
                result["vulnerabilities"].append({
                    "payload": payload,
                    "vector": vectors[i] if i < len(vectors) else "Unknown"
                })

        return result
