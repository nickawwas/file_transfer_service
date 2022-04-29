import io
import mock
from sys import stdout

from client import main

RESET = '\033[0;0m'
FAILED = '\033[1;31m'
SUCCESS = '\033[1;32m'
def write_failed_test(tst):
    stdout.write(FAILED)
    print(f'Failed ✗ - {tst}')
    stdout.write(RESET)

def write_success_test(tst):
    stdout.write(SUCCESS)
    print(f'Passed ✓ - {tst}')
    stdout.write(RESET)

def dummy_input():
    return input("Some input")

def dummy_print():
    print("Some print")

def test_put():
    with mock.patch("builtins.input", return_value="put"):
        assert dummy_input() == "put"
        write_success_test("Only Put Test")

def test_print():
    with mock.patch("sys.stdout", new=io.StringIO()) as test_stdout:
        dummy_print()

    assert test_stdout.getvalue() == "Some print\n"
    write_success_test("Print Test")

def run_tests():
    put_tests = ["put", "put fakeFile", "put sameReport.pdf", "put reportDoc.docx", "put sampleImg.png"]
    get_tests = ["get", "get fakeFile", "get anotherImg.jpeg", "get shortFile.txt", "get sampleVideo.mp4"]
    change_tests = ["change", "change oneFile", "change fake shortFile.txt", "change server.py failed.txt", "change shortFile.txt server.py", "change sampleImg.png newImg_.png"]
    cmds_tests = ["not_real_cmd", "help", "bye"]

    with mock.patch("sys.stdout", new=io.StringIO()) as test_stdout:
        with mock.patch("builtins.input", side_effect=[*put_tests, *get_tests, *change_tests, *cmds_tests]):
            main()
    
    test_output = test_stdout.getvalue()
    actual_outputs = test_output.split("\n\n")

    expected_outputs = [
        'Welcome to FTP Client!', 
        'Error - No File Name Provided!\nusage: put fileName', 'Error - No File with Provided Name on Client!', 'sameReport.pdf was successfully uploaded !', 'reportDoc.docx was successfully uploaded !', 'sampleImg.png was successfully uploaded !',
        'Error - No File Name Provided!\nusage: get fileName', 'Error - File Not Found.\nfakeFile failed to be downloaded !', 'anotherImg.jpeg was successfully downloaded !', 'shortFile.txt was successfully downloaded !', 'sampleVideo.mp4 was successfully downloaded !',
        'Error - New or Old File Name Not Provided!\nusage: change oldFileName newFileName', 'Error - New or Old File Name Not Provided!\nusage: change oldFileName newFileName', 'Error - File Not Found.\nfake failed to be changed to shortFile.txt!', 'Error - Unsuccessful Change.\nserver.py failed to be changed to failed.txt!', 'Error - Unsuccessful Change.\nshortFile.txt failed to be changed to server.py!', 'sampleImg.png was successfully changed to newImg_.png!',
        'Error - Invalid Command.\nSuggestion: Enter help command to view list of commands', 'Cmds: get put change help bye', 'Client Socket Closed!']
    
    test_purpose = [
        "Connected to server socket", 
        "Put command with no filename specified", "Put command with non-existing filename", "Put command with valid pdf", "Put command with valid docx", "Put command with valid png",
        "Get command with no filename specified", "Get command with non-existing filename", "Get command with valid jpeg", "Get command with valid txt", "Get command with valid mp4",
        "Change command with no filenames specified", "Change command with missing filename", "Change command with non-existing filename", "Change command with old critical filename", "Change command with new critical filename", "Change command with valid png filenames",
        "Invalid command entered", "Help command entered", "Close client socket with bye command"]
    
    for actual, expected, purpose in zip(actual_outputs, expected_outputs, test_purpose):
        if actual == expected:
            write_success_test(purpose)
        else:
            write_failed_test(purpose)

run_tests()