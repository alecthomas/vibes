import os
from litellm import completion
import spec
import sys
from typing import List, Protocol
from dataclasses import dataclass
from pygments import highlight
from pygments.lexers import TypeScriptLexer, JsonLexer
from pygments.formatters import TerminalTrueColorFormatter
import posixpath
import argparse
import subprocess

SYSTEM_INSTRUCTIONS = r"""
### **Core Identity and Mission**

You are an expert in TypeScript and specifically Deno. Use the instructions below to assist the user to the best of your
ability.

  * Follow security best practices. Never expose or commit secrets and keys.
  * **IMPORTANT:** Always output code directly, with no other formatting.
  * **IMPORTANT:** Provide plain code WITHOUT markdown formatting or code blocks
  * **IMPORTANT:** DO NOT ADD ANY COMMENTS unless asked.
"""

DEFINITION_INPUT = r"""
### **Background on the system being worked on**

  * This is a Deno project written in TypeScript. We are using Deno v2.3.5 and stdlib 0.224.0.
  * The project is a library with a single function that performs a single task, written in a single file.
  * Only create the function, and any types, etc. that the function requires.
  * The function must take either one or zero values as its input, and return one or zero values as its output.
  * All side-effects must be passed in as function parameters. For example, getting the current time is a side-effect,
    writing to a datastore is a side-effect, and so on. Anything that relies on global state or mutates some external state
    is a side-effect. Do not create named types for injected parameters.
  * The function itself, and all transitive types it uses, must be exported.
  * Don't define defaults for any injected parameters.

Output three files separated by ----:

1. The code for the function.
2. The raw function signature, including any injected types, the name, and any transitive types it uses.
3. The raw function signature with only the input and output types, if any, including the name and any transitive types
   it uses, but excluding any injected functions or types.
"""

TEST_INPUT = r"""
### **Background on the system being worked on**

  * This is a Deno project written in TypeScript. We are using Deno v2.3.5 and stdlib 0.224.0.
  * The project is a library with a single function that performs a single task, written in a single file.
  * Only create the function, and any types, etc. that the function requires.
  * The function must take either one or zero values as its input, and return one or zero values as its output.
  * All side-effects must be passed in as function parameters. For example, getting the current time is a side-effect,
    writing to a datastore is a side-effect, and so on. Anything that relies on global state or mutates some external state
    is a side-effect. Do not create named types for injected parameters.


Write a test for the given function signature. Tests are written similar to the following:

```
import { assertEquals } from "@std/assert";
import { add } from "./main.ts";

Deno.test(function addTest() {
  assertEquals(add(2, 3), 5);
});
```

Write two tests for the function below:

1. A test calling the function directly.
2. A test that sets up a HTTP server and issues a HTTP POST request to the function at http://127.0.0.1:8888/<function-name>

"""

@dataclass
class CodeGenResult:
    code: str
    signature: str
    # Signature of the function excluding injected parameters
    net_signature: str


@dataclass
class TestGenResult:
    test: str


class LLMProvider(Protocol):
    """A Callable type that is the same signature as the "provider" function below, including keyword arguments."""
    def __call__(self, instructions: str, input: str) -> str:
        ...



def generate_code(client: LLMProvider, module_spec: spec.ModuleSpec) -> CodeGenResult:
    response = client(
        instructions=SYSTEM_INSTRUCTIONS,
        input="\n".join([DEFINITION_INPUT, module_spec.definition, "The base function signature follows, but additional injected parameters should be added: ",  module_spec.signature]),
    )
    try:
        code, signature, net_signature = response.split("----\n")
    except Exception as e:
        print(response)
        raise e
    return CodeGenResult(
        code=code,
        signature=signature.strip(),
        net_signature=net_signature.strip(),
    )


def generate_tests(client: LLMProvider, module_spec: spec.ModuleSpec, signature: str) -> List[TestGenResult]:
    out = []
    for test in module_spec.test:
        input = "\n".join([TEST_INPUT, "Function signature:", signature, "Test definition:", test.definition])
        response = client(
            instructions=SYSTEM_INSTRUCTIONS,
            input=input,
        )
        out.append(TestGenResult(response))
    return out


def highlight_ts(code: str) -> str:
    return highlight(code, TypeScriptLexer(), TerminalTrueColorFormatter())


def highlight_json(code: str) -> str:
    return highlight(code, JsonLexer(), TerminalTrueColorFormatter())


def make_provider(model: str) -> LLMProvider:
    """Create a provider function for the given model."""
    def provider(instructions: str, input: str) -> str:
        response = completion(model=model, messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": input},
            ],
            temperature=0.0,
        )
        return response.choices[0].message.content or ""
    return provider


def main():
    parser = argparse.ArgumentParser(description='Generate code from a spec file.')
    parser.add_argument('--model', default='databricks/databricks-claude-sonnet-4', help='The model to use for code generation.')
    parser.add_argument('spec_path', help='The path to the spec file.')
    args = parser.parse_args()

    spec_path = args.spec_path
    module_root = os.path.dirname(spec_path)
    module_spec = spec.load(spec_path)

    provider = make_provider(args.model)

    impl = generate_code(provider, module_spec)
    print(highlight_ts(impl.signature))
    print("---")
    print(highlight_ts(impl.net_signature))
    print("---")
    print(highlight_ts(impl.code))

    tests = generate_tests(provider, module_spec, impl.signature)
    for test in tests:
        print("---")
        print(highlight_ts(test.test))
        # Write test.test to dirname(spec_path) / main_test.ts
        path = os.path.join(module_root, "main_test.ts")
        with open(path, "w") as f:
            f.write(test.test)
        print(f"Wrote {path}")

    # Write impl.code to dirname(spec_path) / main.ts
    path = os.path.join(module_root, "main.ts")
    with open(path, "w") as f:
        f.write(impl.code)
    print(f"Wrote {path}")
    # Execute "deno test --allow-net" in module_root
    print("Executing tests...")
    subprocess.run(["deno", "test", "--allow-net"], cwd=module_root)
    print("Updating spec with signature")
    module_spec.signature = impl.net_signature
    spec.save(spec_path, module_spec)

if __name__ == "__main__":
    main()
