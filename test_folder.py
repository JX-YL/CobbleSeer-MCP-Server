"""生成文件夹版本的资源包"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.builder import Builder
import yaml

config = yaml.safe_load(open('config.yaml', encoding='utf-8'))
builder = Builder(config)

data = {
    'name': 'thunder_wolf',
    'dex': 1002,
    'primary_type': 'Electric',
    'secondary_type': None,
    'stats': {
        'hp': 85,
        'attack': 105,
        'defence': 75,
        'special_attack': 115,
        'special_defence': 80,
        'speed': 120
    },
    'height': 1.2,
    'weight': 45.0,
    'base_friendship': 70
}

files = builder.build_all(data)
result = builder.build_package('thunder_wolf_datapack', files, 'folder')

print(f"文件夹版本已生成: {result['output_path']}")
print(f"请在文件资源管理器中打开此目录查看所有文件")

