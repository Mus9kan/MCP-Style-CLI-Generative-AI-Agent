"""Plugin manager for dynamic tool discovery and loading."""

from pathlib import Path
from typing import Dict, List, Optional, Type
import importlib.util
import sys

from ..utils.logger import get_logger
from ..utils.exceptions import ToolError
from .base import BaseTool
from .registry import ToolRegistry

logger = get_logger(__name__)


class PluginManager:
    """Manages dynamic plugin discovery, loading, and lifecycle."""

    def __init__(self, plugin_dir: Optional[str] = None):
        """
        Initialize plugin manager.
        
        Args:
            plugin_dir: Directory to scan for plugins (default: ~/.cli_agent/plugins)
        """
        if plugin_dir:
            self.plugin_dir = Path(plugin_dir)
        else:
            self.plugin_dir = Path.home() / ".cli_agent" / "plugins"
        
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self.installed_plugins: Dict[str, Dict] = {}
        
        # Auto-discover plugins on init
        self.discover_plugins()

    def discover_plugins(self) -> List[str]:
        """
        Scan plugin directory for .py files and register them.
        
        Returns:
            List of discovered plugin names
        """
        discovered = []
        
        for plugin_file in self.plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue
            
            try:
                plugin_name = plugin_file.stem
                self._load_plugin_module(plugin_name, plugin_file)
                discovered.append(plugin_name)
                logger.info(f"Discovered plugin: {plugin_name}")
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_name}: {e}")
        
        return discovered

    def _load_plugin_module(self, plugin_name: str, plugin_file: Path) -> None:
        """
        Dynamically load a plugin module.
        
        Args:
            plugin_name: Name of the plugin
            plugin_file: Path to plugin file
        """
        # Load module from file
        spec = importlib.util.spec_from_file_location(f"cli_agent.plugins.{plugin_name}", plugin_file)
        if not spec or not spec.loader:
            raise ToolError("plugin_manager", f"Invalid plugin spec: {plugin_name}")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"cli_agent.plugins.{plugin_name}"] = module
        spec.loader.exec_module(module)
        
        # Find and register tool classes in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseTool)
                and attr != BaseTool
                and hasattr(attr, 'name')
            ):
                # Register the tool
                ToolRegistry.register(attr)
                self.installed_plugins[plugin_name] = {
                    "file": str(plugin_file),
                    "tools": [attr.name],
                    "status": "active",
                }
                logger.info(f"Registered tool from plugin: {attr.name}")

    def install_plugin(self, plugin_name: str, source_url: Optional[str] = None) -> bool:
        """
        Install a plugin from various sources.
        
        Args:
            plugin_name: Name of the plugin
            source_url: URL to download from (GitHub, etc.)
            
        Returns:
            True if installation successful
        """
        # For now, this is a placeholder
        # In a full implementation, you'd:
        # 1. Download from GitHub/GitLab
        # 2. Validate the plugin
        # 3. Install dependencies
        # 4. Load the plugin
        
        plugin_file = self.plugin_dir / f"{plugin_name}.py"
        
        if not plugin_file.exists():
            logger.error(f"Plugin file not found: {plugin_file}")
            return False
        
        # Load the plugin
        self._load_plugin_module(plugin_name, plugin_file)
        logger.info(f"Plugin installed: {plugin_name}")
        
        return True

    def uninstall_plugin(self, plugin_name: str) -> bool:
        """
        Uninstall a plugin.
        
        Args:
            plugin_name: Name of the plugin to remove
            
        Returns:
            True if uninstallation successful
        """
        plugin_file = self.plugin_dir / f"{plugin_name}.py"
        
        if not plugin_file.exists():
            logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        # Remove tools registered by this plugin
        if plugin_name in self.installed_plugins:
            plugin_info = self.installed_plugins[plugin_name]
            for tool_name in plugin_info.get("tools", []):
                # Note: ToolRegistry doesn't have unregister yet
                logger.warning(f"Tool {tool_name} still registered (restart required)")
            
            del self.installed_plugins[plugin_name]
        
        # Remove file
        plugin_file.unlink()
        logger.info(f"Plugin uninstalled: {plugin_name}")
        
        return True

    def list_plugins(self) -> List[Dict]:
        """
        List all installed plugins.
        
        Returns:
            List of plugin information dictionaries
        """
        plugins = []
        
        for name, info in self.installed_plugins.items():
            plugins.append({
                "name": name,
                "file": info["file"],
                "tools": info["tools"],
                "status": info["status"],
            })
        
        return plugins

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict]:
        """
        Get information about a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin information or None
        """
        return self.installed_plugins.get(plugin_name)
