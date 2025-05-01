import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

class ConfigManager:
    def __init__(self):
        # 配置文件保存在当前工程目录下的configs文件夹
        self.config_dir = Path(__file__).parent.parent / "configs"
        self.config_dir.mkdir(exist_ok=True)
        
    def get_config_path(self, config_name: str) -> Path:
        """获取配置文件的完整路径"""
        return self.config_dir / f"{config_name}.json"
        
    def save_config(self, config_name: str, config_data: Dict) -> bool:
        """保存配置到指定名称的文件"""
        try:
            config_path = self.get_config_path(config_name)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
            
    def load_config(self, config_name: str) -> Optional[Dict]:
        """从指定名称的文件加载配置"""
        try:
            config_path = self.get_config_path(config_name)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"加载配置失败: {e}")
            return None
            
    def list_configs(self) -> List[str]:
        """列出所有可用的配置名称"""
        configs = []
        for f in self.config_dir.glob("*.json"):
            configs.append(f.stem)
        return sorted(configs)
            
    def save_hero_selection(
        self,
        config_name: str,
        selected_heroes: List[str],
        special_cards: List[str],
        d_count: int
    ) -> bool:
        """保存英雄选择配置到指定名称"""
        config = {
            "selected_heroes": selected_heroes,
            "special_cards": special_cards,
            "d_count": d_count,
            "version": "1.0"
        }
        return self.save_config(config_name, config)
        
    def load_hero_selection(self, config_name: str) -> Optional[Dict]:
        """从指定名称加载英雄选择配置"""
        config = self.load_config(config_name)
        if config:
            return {
                "selected_heroes": config.get("selected_heroes", []),
                "special_cards": config.get("special_cards", []),
                "d_count": config.get("d_count", 10)
            }
        return None
        
    def delete_config(self, config_name: str) -> bool:
        """删除指定名称的配置"""
        try:
            config_path = self.get_config_path(config_name)
            if config_path.exists():
                config_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"删除配置失败: {e}")
            return False
