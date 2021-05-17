def purport_replacements(purport):
    purport = purport.replace('</p>', '---')
    purport = purport.replace('[<div class="purport">', '')
    purport = purport.replace('<p>', '')
    purport = purport.replace('<i>', '')
    purport = purport.replace('</i>', '')
    purport = purport.replace('</div>]', '')
    purport = purport.replace('</dl>', '---')
    purport = purport.replace('<dl>', 'verse>>>')
    purport = purport.replace('<dd>', '')
    purport = purport.replace('</dd>', '')

    return purport