import re

content = """## All Vices Offend Against Love

<div class="audio-only">
Every vice represents a rejection or distortion of the four pillars of perfect love. While some vices may seem to attack one pillar more than others, most sins involve a collapse of the entire structure of love.

For instance, **Pride** is not just an offense against **Truth** (denying our dependence on God); it is also an offense against **Justice** (stealing God's glory), **Mercy** (judging others), and **Sacrifice** (refusing to serve). Similarly, **Lust** is not just a failure of **Sacrifice** (self-control); it distorts the **Truth** of the body, violates **Justice** by using persons as objects, and refuses **Mercy** by prioritizing pleasure over another's good.

Understanding this helps us see that sin is not just "breaking a rule"—it is breaking the bonds of communion that love creates.
</div>

<div class="print-only">
The following matrix shows which pillar(s) each vice primarily offends against. A "✗" indicates the vice primarily offends against that pillar.

| Vice | Truth | Justice | Mercy | Sacrifice |
|------|-------|---------|-------|-----------|
| **Opposing Theological Virtues** |
| Unbelief/Infidelity | ✗ | ✗ | | ✗ |
</div>
"""

def filter_conditional_content(text, profile):
    print(f"Testing profile: {profile}")
    print("-" * 20)

    # Pattern from bin/build
    print_pattern = re.compile(r'<div[^>]*class=["\']print-only["\'][^>]*>(.*?)</div>', re.DOTALL | re.IGNORECASE)
    audio_pattern = re.compile(r'<div[^>]*class=["\']audio-only["\'][^>]*>(.*?)</div>', re.DOTALL | re.IGNORECASE)

    def unwrap(match):
        return match.group(1).strip()

    is_audio = (profile and "audio" in profile)

    if is_audio:
        print("Mode: Audio (removing print-only, keeping audio-only)")
        text = print_pattern.sub('', text)
        text = audio_pattern.sub(unwrap, text)
    else:
        print("Mode: Print (removing audio-only, keeping print-only)")
        text = audio_pattern.sub('', text)
        text = print_pattern.sub(unwrap, text)

    print("Result length:", len(text))
    print("Contains 'Every vice represents':", "Every vice represents" in text)
    print("Contains 'The following matrix shows':", "The following matrix shows" in text)
    print("-" * 20)
    return text

# Test scenarios
filter_conditional_content(content, "audiotxt")
filter_conditional_content(content, "audiopdf")
filter_conditional_content(content, "default")
