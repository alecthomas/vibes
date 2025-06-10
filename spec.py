import tomlkit
from typing import List
from dataclasses import dataclass

@dataclass
class Test:
    definition: str


@dataclass
class ModuleSpec:
    signature: str
    definition: str
    test: List[Test]
    _original_toml: tomlkit.TOMLDocument


def load(file_path: str) -> ModuleSpec:
    """
    Load and parse a module specification TOML file using tomlkit.

    Args:
        file_path: Path to the TOML file

    Returns:
        ModuleSpec object containing parsed data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = tomlkit.load(f)

    # Parse signature and definition
    signature = data.get('signature', '')
    definition = data.get('definition', '')

    # Parse tests
    tests = []
    for test_data in data.get('test', []):
        test = Test(
            definition=test_data.get('definition'),
        )
        tests.append(test)

    return ModuleSpec(signature=signature, definition=definition, test=tests, _original_toml=data)


def save(path: str, spec: ModuleSpec):
    if 'signature' not in spec._original_toml:
        spec._original_toml['signature'] = tomlkit.string(spec.signature, multiline=True)
    if 'definition' not in spec._original_toml:
        spec._original_toml['definition'] = tomlkit.string(spec.definition, multiline=True)

    with open(path, 'w', encoding='utf-8') as f:
        tomlkit.dump(spec._original_toml, f)
