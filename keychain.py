import subprocess, re

class Keychain:
    class KeychainItem:
        search_atts = {
            'title': r'^\s*0x00000007 <blob>="([^"]*)"$',
            'server': r'^\s*"srvr"<blob>="([^"]*)"$',
            'account': r'\s*"acct"<blob>="([^"]*)"$',
            'keychain': r'^keychain: "([^"]*)"$'
        }

        __flags = {
            'title': '-l',
            'server': '-s',
            'account': '-a',
            'keychain': ''
        }

        def __init__(self, attributes):
            self.attributes = {
                key: (lambda m: m.group(1) if m else None)(re.search(reg, attributes, re.MULTILINE))
            for key, reg in Keychain.KeychainItem.search_atts.items() }
        
        def copy_password(self):
            args = ' '.join([
                f"{Keychain.KeychainItem.__flags[key]} '{self.attributes[key]}'"
            for key in Keychain.KeychainItem.search_atts.keys() if self.attributes[key]])
            if subprocess.run([f"security find-internet-password -w {args} | tr -d '\n' | pbcopy"], capture_output=True, shell=True).stderr:
                subprocess.run([f"security find-generic-password -w {args} | tr -d '\n' | pbcopy"], shell=True)

        
    splitter = 'keychain: '

    def __init__(self, keychains):
        dumped = ''.join([
            subprocess.check_output(f'security dump-keychain {keychain}', shell=True).decode('utf-8')
        for keychain in keychains])
        self.kc_items = self.__parse(dumped)
    
    def __parse(self, dumped):
        return [
            Keychain.KeychainItem(Keychain.splitter + block)
        for block in dumped.split(Keychain.splitter) if block]

    def find_first(self, query, count = 1):
        if not query or query == ' ': return []
        res = list()
        for kc_item in self.kc_items:
            if [item for item in kc_item.attributes.values() if item and query in item]:
                res.append(kc_item)
                if len(res) == count: return res
        return res

