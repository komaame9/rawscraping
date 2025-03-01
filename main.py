import db_model
#import argparse

def main():
    #parser = argparse.ArgumentParser()
    #parser.add_argument("-u", "--update", help="scrape site and update database file", action="store_true")
    #args = parser.parse_args()

    db_model.update_all_pages()

if __name__ == "__main__":
    main()

