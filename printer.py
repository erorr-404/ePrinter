import subprocess
from PyPDF2 import PdfReader, PdfWriter

PRINTER_NAME = "hp LaserJet 1010 HB"  # needed printer name
ADOBE_PATH = "C:\\Program Files\\Adobe\\Acrobat DC\\Acrobat\\Acrobat.exe"  # Adobe Acrobat path


# separates the even and odd pages, and save them into two new PDF files
def divide(file_path: str) -> (str, str):
    # read the PDF
    pdf_reader = PdfReader(file_path)

    # Create two PDF writers for even and odd pages
    even_writer = PdfWriter()
    odd_writer = PdfWriter()

    # Loop through the pages and categorize them
    for i in range(len(pdf_reader.pages)):
        if (i + 1) % 2 == 0:  # Page numbers are 1-based
            even_writer.add_page(pdf_reader.pages[i])
        else:
            odd_writer.add_page(pdf_reader.pages[i])

    # Write the odd pages to a new PDF file
    with open(file_path + "_odd", "wb") as odd_file:
        odd_writer.write(odd_file)

    # Write the even pages to a new PDF file
    with open(file_path+"_even", "wb") as even_file:
        even_writer.write(even_file)

    return file_path + "_odd", file_path+"_even"


# Example: start_printing("C:\\Users\\maxym\\Desktop\\test2.pdf")
# run command to open Adobe Acrobat and print the file
def start_printing(file_path: str) -> bool:
    # create command
    command = [
        ADOBE_PATH,
        "/P",
        file_path
    ]

    # run command, catch error if it is and return True if there is no errors
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print("An error occured:", e)
        return False