# -*- coding: utf-8 -*-
"""
Yardımcı fonksiyonlar
"""

def turkish_to_english_chars(text):
    """Türkçe karakterleri İngilizce karşılıklarına dönüştürür"""
    if not text:
        return text
    
    char_map = {
        'ç': 'c', 'Ç': 'C',
        'ğ': 'g', 'Ğ': 'G', 
        'ı': 'i', 'I': 'I',
        'İ': 'I', 'i': 'i',
        'ö': 'o', 'Ö': 'O',
        'ş': 's', 'Ş': 'S',
        'ü': 'u', 'Ü': 'U'
    }
    
    result = text
    for tr_char, en_char in char_map.items():
        result = result.replace(tr_char, en_char)
    
    return result
