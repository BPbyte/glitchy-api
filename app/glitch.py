import random

def glitch_text(text, style):
    if style == "zalgo":
        return zalgo(text)
    elif style == "ascii":
        return ascii_art(text)
    elif style == "vaporwave":
        return vaporwave(text)
    elif style == "chaos":
        return chaos(text)
    elif style == "blockchain":
        return blockchain(text)
    return text

def glitch_preview(text, style):
    # Simplified preview, truncated for non-paid users
    return glitch_text(text[:10], style) + "..." if len(text) > 10 else glitch_text(text, style)

def zalgo(text):
    zalgo_chars = [chr(i) for i in range(768, 879)]
    result = ""
    for char in text:
        result += char + "".join(random.choice(zalgo_chars) for _ in range(2))
    return result

def ascii_art(text):
    mapping = {"a": "█", "b": "▓", "c": "▒", "d": "▚", "e": "▞"}
    return "".join(mapping.get(c.lower(), c) for c in text)

def vaporwave(text):
    full_width = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
    )
    return text.translate(full_width)

def chaos(text):
    styles = [zalgo, ascii_art, vaporwave]
    return "".join(random.choice(styles)(c) for c in text)

def blockchain(text):
    return "0x" + "".join(f"{ord(c):02x}" for c in text)