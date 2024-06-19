import requests
from xmldiff import main

# URLs of the XSD files
url_a = 'https://webstds.ipc.org/2581/IPC-2581A.xsd'
url_b = 'https://webstds.ipc.org/2581/IPC-2581B.xsd'
url_b1 = 'https://webstds.ipc.org/2581/IPC-2581B1.xsd'
url_c = 'https://webstds.ipc.org/2581/IPC-2581C.xsd'
# url-s to xsd files
def download_file(url, filename):
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful
    with open(filename, 'wb') as file:
        file.write(response.content)
    print(f'Downloaded {filename}')

download_file(url_a, 'IPC-2581A.xsd')
download_file(url_b, 'IPC-2581B.xsd')
download_file(url_b1, 'IPC-2581B1.xsd')
download_file(url_c, 'IPC-2581C.xsd')

# Compare the chosen two XSD files(change their names, if you want to compare other files)
diff = main.diff_files('IPC-2581A.xsd', 'IPC-2581C.xsd')
#print('\nDifferences:')
#for change in diff:
    #print(change)

output_filename = 'A-C changes.txt'
with open(output_filename, 'w', encoding='utf-8') as file:
    file.write('Differences between IPC-2581A and IPC-2581C:\n')

    # counters for different operations
    insert_count = 0
    update_count = 0
    delete_count = 0
    rename_count = 0
    move_count = 0

    # count different kinds of changes
    for change in diff:
        if change.__class__.__name__ == 'InsertNode':
            insert_count += 1
        elif change.__class__.__name__ == 'UpdateAttrib':
            update_count += 1
        elif change.__class__.__name__ == 'DeleteAttrib':
            delete_count += 1
        elif change.__class__.__name__ == 'RenameNode':
            rename_count += 1
        elif change.__class__.__name__ == 'MoveNode':
            move_count += 1

    file.write('\nOperation Counts:\n')
    file.write(f'Insert operations: {insert_count}\n')
    file.write(f'Update operations: {update_count}\n')
    file.write(f'Delete operations: {delete_count}\n')
    file.write(f'Rename operations: {rename_count}\n')
    file.write(f'Move operations: {move_count}\n')
    #write all the changes only to file
    for change in diff:
        file.write(str(change) + '\n')

print(f'Insert operations: {insert_count}')
print(f'Update operations: {update_count}')
print(f'Delete operations: {delete_count}')
print(f'Rename operations: {rename_count}')
print(f'Move operations: {move_count}')

