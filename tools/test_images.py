import urllib.request

urls = {
    "quinoa": "https://images.unsplash.com/photo-1586201375761-83865001e31c",
    "brown_rice": "https://images.unsplash.com/photo-1628108647716-43b679b32c61",
    "edamame": "https://images.unsplash.com/photo-1568285521998-e325fc06b744",
    "salmon": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2",
    "chicken": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d",
    "falafel": "https://images.unsplash.com/photo-1593001874117-c99c800e3eb7",
    "sweet_potato": "https://images.unsplash.com/photo-1596097635121-14b63b7a0c19",
    "lemon": "https://images.unsplash.com/photo-1587496679742-bad502958fbf",
    "wheatgrass": "https://images.unsplash.com/photo-1611162458324-aae1eb4129a4",
    "charcoal": "https://images.unsplash.com/photo-1616853503612-4211181fdfd2",
    "aloe": "https://images.unsplash.com/photo-1595981267035-7b04d84b5228",
    "lemon2": "https://images.unsplash.com/photo-1568569350062-ebfa3cb195df",
    "aloe2": "https://images.unsplash.com/photo-1600180766352-1ce8a95632d4"
}

for name, url in urls.items():
    try:
        req = urllib.request.Request(url + "?w=150&h=150&fit=crop", headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req)
        print(f"{name}: OK")
    except Exception as e:
        print(f"{name}: FAILED - {e}")
