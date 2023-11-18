from datetime import datetime
from pylaform.utilities.dbConnector import Queries
from pylatex import escape_latex, NoEscape
import re


class Commands:
    """
    Package of commands build from pylatex
    :return: None
    """

    def __init__(self):
        self.queries = Queries()

    @staticmethod
    def unique(list1):
        """
        Returns only unique values of a list
        :param list list1: source list
        :return: list
        """
        # initialize a null list
        unique_list = []

        # traverse for all elements
        for x in list1:
            # check if exists in unique_list or not
            if x not in unique_list:
                unique_list.append(x)

        return unique_list

    @staticmethod
    def format_date(date_date):
        """
        Reformat ('YYYY-MM-DD') into 'Month - Year'
        :param Any date_date:
        :return: str
        """
        if date_date is None:
            return "Present"
        return datetime.strftime(date_date, "%B %Y")

    @staticmethod
    def hyperlink(url, text):
        """
        Create a hyperlink in the document
        :param str url:
        :param str text:
        :return: object
        """
        text = escape_latex(text)
        return NoEscape(r'\href{' + url + '}{' + text + '}')

    @staticmethod
    def textbox(short, long):
        concat = NoEscape(
            r"\pdfmarkupcomment[markup=Underline,opacity=0.2]{"
            + f"{short}"
            + r"}{"
            + f"{long}"
            + r"}")
        return concat

    @staticmethod
    def vspace(size):
        return NoEscape(r"\vspace{" + size + r" in}")

    @staticmethod
    def hspace(size):
        return NoEscape(r"\nobreak\hspace{" + str(size) + r" em}")

    def glossary_inject(self, text):
        """
        Scan source text for matching substrings and add pdfcomments to them.
        :param str text: source text
        :return: Any
        """

        glossary = self.queries.glossary()
        search_terms = Commands.unique([sub['term'] for sub in glossary])
        updated_text = r"" + text
        for term in search_terms:
            if re.search(term, text):
                term_sub = re.compile(r'(?P<all>(\w*)\s*' + re.escape(term) + r'\s*(\w*))')
                rez = [m.groupdict() for m in term_sub.finditer(updated_text)]
                for item in rez:
                    print(item["all"])
                updated_text = updated_text.replace(
                    term, Commands.textbox(
                        term, [sub['description'] for sub in glossary if sub['term'] == term][0]))

        return updated_text