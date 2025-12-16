#!/usr/bin/env python3
"""
Test script to verify prompt templates work correctly
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from chains import load_prompt_template
    from langchain_core.prompts import PromptTemplate

    # Test loading prompts
    prompts = ['data_collector', 'writer', 'feedback', 'modificator']

    for prompt_name in prompts:
        try:
            prompt_text = load_prompt_template(prompt_name)
            print(f"✅ Loaded {prompt_name} prompt successfully")

            # Try to create PromptTemplate to check for variable parsing issues
            # We'll extract variables from the text to test
            import re
            variables = re.findall(r'\{(\w+)\}', prompt_text)
            unique_vars = list(set(variables))

            print(f"   Found variables: {unique_vars}")

            # Test creating the template
            template = PromptTemplate(
                template=prompt_text,
                input_variables=unique_vars
            )
            print(f"   ✅ Template created successfully for {prompt_name}")

        except Exception as e:
            print(f"❌ Error with {prompt_name}: {e}")

    print("\n🎉 All prompt tests completed!")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")



