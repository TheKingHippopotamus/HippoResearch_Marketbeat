#!/usr/bin/env python3
"""
Demo script showing how to use the integrated feedback system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.feedback_processor import get_feedback_processor, integrate_feedback_with_prompt
from tools.llm_processor import process_with_quality_check
from tools.entity_analyzer import analyze_text_for_llm_with_cache

def demo_feedback_processor():
    """Demonstrate the feedback processor functionality"""
    print("🔍 Demo: Feedback Processor")
    print("=" * 50)
    
    # Get feedback processor
    processor = get_feedback_processor()
    
    # Show all rules
    print(f"📋 Loaded {len(processor.get_all_rules())} feedback rules")
    
    # Show rules by category
    for category, rules in processor.categorized_rules.items():
        print(f"\n📂 {category.upper()} ({len(rules)} rules):")
        for rule in rules[:2]:  # Show first 2 rules per category
            print(f"  - {rule.error_type}: {rule.rule[:60]}...")
    
    # Generate thinking prompt
    sample_text = """
    Abbott Laboratories (ABT) reported strong Q4 earnings with revenue growth of 8.5%.
    The company's EPS guidance was lowered from $4.50 to $4.45 for 2024.
    Analysts remain bullish on the stock with a price target of $120.
    """
    
    print(f"\n🧠 Generated Thinking Prompt:")
    thinking_prompt = processor.generate_thinking_prompt(sample_text, "ABT")
    print(thinking_prompt[:300] + "...")

def demo_integrated_processing():
    """Demonstrate integrated processing with feedback"""
    print("\n\n🔄 Demo: Integrated Processing")
    print("=" * 50)
    
    sample_text = """
    [positive] DoorDash (DASH) reported Q4 revenue of $2.3B, up 27% YoY
    [positive] Active users increased to 32M, beating estimates
    [negative] EPS guidance lowered from $1.20 to $1.15 for 2024
    [neutral] Company expanding to new markets in Europe
    """
    
    print("📝 Sample text for processing:")
    print(sample_text)
    
    # Process with quality check
    result = process_with_quality_check(
        text_block=sample_text,
        ticker_symbol="DASH",
        article_type="default"
    )
    
    print(f"\n✅ Processing completed:")
    print(f"  - Initial translation length: {len(result['initial_translation'])} chars")
    print(f"  - Quality check applied: {result['needs_review']}")
    
    if result['quality_check_prompt']:
        print(f"\n🔍 Quality Check Prompt:")
        print(result['quality_check_prompt'][:400] + "...")

def demo_entity_analysis_with_feedback():
    """Demonstrate entity analysis with feedback integration"""
    print("\n\n🔍 Demo: Entity Analysis with Feedback")
    print("=" * 50)
    
    sample_text = """
    Microsoft (MSFT) announced acquisition of Activision Blizzard for $68.7B.
    The deal faces regulatory scrutiny in multiple jurisdictions.
    Analysts expect the acquisition to close by end of 2024.
    """
    
    print("📝 Sample text for entity analysis:")
    print(sample_text)
    
    # Analyze with entity analyzer
    entity_context = analyze_text_for_llm_with_cache(sample_text, "MSFT")
    
    print(f"\n🔍 Entity Analysis Context:")
    print(entity_context[:500] + "...")

def main():
    """Run all demos"""
    print("🚀 Feedback System Integration Demo")
    print("=" * 60)
    
    try:
        demo_feedback_processor()
        demo_integrated_processing()
        demo_entity_analysis_with_feedback()
        
        print("\n\n✅ All demos completed successfully!")
        print("\n💡 Key Benefits of Integration:")
        print("  - 🧠 Thinking prompts improve translation quality")
        print("  - 🔍 Quality checks catch common errors")
        print("  - 📋 Feedback rules guide the model")
        print("  - 🔄 Iterative improvement process")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 