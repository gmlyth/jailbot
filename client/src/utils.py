async def get_hostname(address):
    address = address.replace("http://","")
    address = address.replace("https://","")
    address = address.replace("www.", "") # May replace some false positives ('www.com')
    result = address.split('/')[0]
    return result