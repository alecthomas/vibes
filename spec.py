import tomlkit
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Test:
    fake: Optional[str] = None
    input: str = ""
    output: str = ""

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
            fake=test_data.get('fake'),
            input=test_data.get('input', ''),
            output=test_data.get('output', '')
        )
        tests.append(test)

    return ModuleSpec(signature=signature, definition=definition, test=tests, _original_toml=data)


def save(path: str, spec: ModuleSpec):
    # Save the spec to path, updating the _original_toml document from the fields of the spec.
    spec._original_toml['signature'] = spec.signature
    spec._original_toml['definition'] = spec.definition

    with open(path, 'w', encoding='utf-8') as f:
        tomlkit.dump(spec._original_toml, f)
