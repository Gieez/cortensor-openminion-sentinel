"""Utility script to patch OpenMinion 0.1.4 Cortensor provider adapter.

Issue in OpenMinion 0.1.4:
In `openminion.modules.llm.providers.cortensor.adapter._build_openai_chat_payload`,
the `"stream": False` key was omitted. OpenAI-compatible proxies and servers that
default to SSE streaming will stream chunks, causing the non-streaming JSON reader
to wait indefinitely or fail.

This script patches the installed package in site-packages if needed.
"""

import sys
from pathlib import Path


def patch_openminion():
    try:
        import openminion.modules.llm.providers.cortensor.adapter as adapter_module
    except ImportError:
        print("[!] OpenMinion package not found in current environment. Install openminion first.")
        return False

    target_file = Path(adapter_module.__file__)
    print(f"[*] Checking {target_file} ...")
    content = target_file.read_text(encoding="utf-8")

    if 'payload["stream"] = False' in content:
        print("[+] OpenMinion Cortensor provider is already patched with payload['stream'] = False.")
        return True

    target_str = 'max_tokens = self._resolve_max_tokens(request=request, config=config)\n        payload["max_tokens"] = int(max_tokens)'
    replacement = target_str + '\n        payload["stream"] = False'

    if target_str in content:
        new_content = content.replace(target_str, replacement, 1)
        target_file.write_text(new_content, encoding="utf-8")
        print("[+] Successfully patched OpenMinion Cortensor provider adapter!")
        return True
    else:
        print("[!] Could not find target pattern in adapter.py (different OpenMinion version?).")
        return False


if __name__ == "__main__":
    success = patch_openminion()
    sys.exit(0 if success else 1)
