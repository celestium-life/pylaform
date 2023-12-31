from pylaform.commands.db.query import Get
from pylaform.commands.latex import Commands
from pylaform.utilities.commands import contact_flatten, listify, slim, unique
from pylatex import Itemize, NewLine, Section, Subsection, Tabular, Tabularx, Document
from pylatex.utils import bold, italic, NoEscape


class Common:
    """
    Common methods used to generate ports of the resume that are shared between templates.
    :return None: None
    """

    def __init__(self) -> None:
        self.resume_data = Get()
        self.cmd = Commands()

    def modern_contact_header(self, doc: Document) -> None:
        """
        Print header containing the modern contact information.
        :param Document doc: PyLatex document handler.
        :return None: None
        """

        # Setup values.
        data: dict[str, dict[str, str | bool]] = contact_flatten(self.resume_data.get_identification())
        phone: str = data["phone"]["value"]
        phone_number: str = f"({phone[0:3]}) {phone[3:6]}-{phone[6:10]}"
        
        # Start writing.
        with doc.create(Section(data["name"]["value"] if data["name"]["state"] else "", False)):
            doc.append(self.cmd.vspace("-0.12"))
            with doc.create(Tabularx("X X")) as table1:
                table1.add_hline()
                table1.add_row((
                    self.cmd.hyperlink(
                        data["www"]["value"] if data["www"]["state"] else "",
                        "https://"
                        + data["www"]["value"] if data["www"]["state"] else ""),
                    "",
                ))
            doc.append(self.cmd.vspace("-0.1"))
            doc.append(self.cmd.hspace("-24.0"))
            with doc.create(Tabular("r r r")) as table2:
                table2.add_row(
                    f"{phone_number if data['phone']['state'] else ''}",
                    f"{data['email']['value'] if data['email']['state'] else ''}",
                    f"{data['location']['value'] if data['location']['state'] else ''}")

    def retro_contact_header(self, doc: Document) -> None:
        """
        Print header containing the retro contact information.
        :param Document doc: PyLatex document handler.
        :return None: None
        """

        # Setup values.
        data: dict[str, dict[str, str | bool]] = contact_flatten(self.resume_data.get_identification())
        name: str = data["name"]["value"]
        phone: str = data["phone"]["value"]
        phone_number: str = italic("Phone:  ") + f"({phone[0:3]}) {phone[3:6]}-{phone[6:10]}"
        email: str = italic("E-mail:  ") + self.cmd.hyperlink(
                data["email"]["value"], "mailto:" + data["email"]["value"])
        www: str = italic("WWW: ") + self.cmd.hyperlink(
            data["www"]["value"], "https://" + data["www"]["value"])

        # Start writing.
        doc.append(NoEscape(r"\name{" + f"{name if data['name']['state'] else ''}" + r"}") + self.cmd.vspace("0.1"))
        doc.append(NoEscape(r"\begin{resume}"))
        doc.append(NoEscape(r"\section{\sc Contact Information}"))
        doc.append(self.cmd.vspace(".05"))
        with doc.create(Tabular("l")) as table1:
            table1.add_row([NoEscape(phone_number if data["phone"]["state"] else "")])
            table1.add_row([NoEscape(email if data["email"]["state"] else "")])
            table1.add_row([NoEscape(www if data["www"]["state"] else "")])

    def modern_summary_details(self, doc: Document) -> None:
        """
        Print detailed modern summary.
        :param Document doc: PyLatex document handler.
        :return None: None
        """

        summaries: list[dict[str, str | bool]] = slim(self.resume_data.get_summary())
        
        # Start writing.
        with (doc.create(Section("Summary", False))) as summary_sub:
            for summary in summaries:
                summary_sub.append(NoEscape(r"\begin{itemize}"))
                summary_sub.append(NoEscape(r"\item\textbf{" + summary["shortdesc"] + r":} "
                                            + self.cmd.glossary_inject(summary["longdesc"], "modern")))
                summary_sub.append(NoEscape(r"\end{itemize}"))

    def retro_summary_details(self, doc: Document) -> None:
        """
        Print detailed retro summary.
        :param Document doc: PyLatex document handler.
        :return None: None
        """

        summaries: list[dict[str, str | bool]] = slim(self.resume_data.get_summary())
        
        # Start writing
        doc.append(NoEscape(r"\section{\sc Summary}"))
        for summary in summaries:
            doc.append(NoEscape(
                r"\textbf{" + summary["shortdesc"] + r":} " 
                + self.cmd.glossary_inject(summary["longdesc"], "retro")))
            doc.append(NewLine())

    def modern_skills(self, doc: Document) -> None:
        """
        Print detailed modern professional_experience.
        :param Document doc: PyLatex document handler.
        :return None: None
        """

        # Remove all items designated to be hidden
        unique_categories: list[dict[str, str, str, int, str, int, str, str]] = unique(
            [{"id": sub["id"], "attr": sub["attr"], "value": sub["value"], "state": sub["state"]}
             for sub in self.resume_data.get_skills()])
        skills: list[dict[str, str | bool]] = slim(self.resume_data.get_skills())

        category_item_count = []
        skill_item_count = []
        for item in unique_categories:
            category_item_count.append(item["attr"])
        for item in skills:
            skill_item_count.append(item["subcategory"])
        unique_list = unique(skill_item_count)
        counts_dict = {}
        for item in unique_list:
            counts_dict.update({item: Common.count_instances(skill_item_count, item)})

        # Start writing.
        with ((doc.create(Section("Skills", False)))):
            categories = slim(self.resume_data.get_skills())
            current_subcategory = ""
            sub_category = []
            for i, category in enumerate(categories, 1):
                if category["subcategory"] != current_subcategory and category["subcategory"] not in sub_category:
                    current_subcategory = category["subcategory"]
                    sub_category.append(category["subcategory"])
                    # if i % last_run == 0:
                    with doc.create(Subsection(category["subcategory"], False)) as skill_sub:
                        skill_sub.append(NoEscape(r"\begin{itemize*}"))
                        skill_counter = 1
                        for skill in skills:
                            if (skill["category"] == category["category"]
                                    and skill["subcategory"] == category["subcategory"]):
                                skill_sub.append(NoEscape(r"\item")
                                                 + self.cmd.textbox(skill["shortdesc"], skill["longdesc"]))
                                if skill_counter == counts_dict[category["subcategory"]]:
                                    skill_sub.append(NoEscape(r"\end{itemize*}"))
                                    break
                                else:
                                    skill_counter = skill_counter + 1

    def retro_skills(self, doc: Document) -> None:
        """
        Print detailed retro professional_experience.se
        :param Document doc: PyLatex document handler.
        :return None: None
        """

        doc.append(NoEscape(r"\section{\sc Experience}"))

        categories = unique([sub["category"] for sub in slim(self.resume_data.get_skills())])
        subcategories = unique([{"subcategory": sub["subcategory"], "category": sub["category"]}
                                for sub in listify(self.resume_data.get_skills())])
        for category in categories:
            doc.append(bold(category))
            for subcategory in subcategories:

                # Start writing.
                if category == subcategory["category"]:
                    doc.append(NewLine())
                    doc.append(NoEscape(r"{\textit {" + subcategory["subcategory"] + r"}}"))
                    doc.append(NoEscape(r"\begin{list2}"))
                    for skill in listify(self.resume_data.get_skills()):
                        if subcategory["subcategory"] == skill["subcategory"]:
                            doc.append(NoEscape(
                                r"\item " + self.cmd.glossary_inject(skill["longdesc"], "retro")))
                    doc.append(NoEscape(r"\end{list2}"))

    def modern_work_history(self, doc: Document) -> None:
        """
        Print standard detail work history.
        :param Document doc: PyLatex document handler.
        :return None: None
        """

        # Start writing.
        with ((doc.create(Section("Employment", False)))):
            companies = slim(self.resume_data.get_achievements())
            current_subcategory = ""
            sub_category = []
            for employer in companies:
                if employer["employer"] != current_subcategory and employer["employer"] not in sub_category:
                    current_subcategory = employer["employer"]
                    sub_category.append(employer["employer"])
                    employer_name = self.resume_data.query_name(employer["employer"], "employer")
                    with doc.create(Subsection(employer_name, False)):
                        for position in unique(listify(self.resume_data.get_positions())):
                            if employer["employer"] == position["employer"]:
                                position_name = self.resume_data.query_name(position["position"], "position")
                                with doc.create(Subsection(position_name, False)) as position_sub:
                                    position_sub.append(self.cmd.vspace("-0.25"))
                                    end_date = "Present" if self.cmd.format_date(
                                        position["enddate"]) == "" else self.cmd.format_date(position["enddate"])
                                    position_sub.append(NoEscape(
                                        r"\hfill{\textbf{"
                                        + f"{self.cmd.format_date(position['startdate'])} "
                                        + r"{--} "
                                        + end_date
                                        + r"}}"))
                                    position_sub.append(NewLine())
                                    for achievement in unique(listify(self.resume_data.get_achievements())):
                                        if position["employer"] == achievement["employer"] and (
                                                position["position"] == achievement["position"]):
                                            with doc.create(Itemize()) as itemize:
                                                itemize.add_item(NoEscape(
                                                    self.cmd.glossary_inject(
                                                        achievement["shortdesc"], "modern")))

    def retro_work_history(self, doc: Document) -> None:
        """
        Print standard detail work history, however for res.cls.
        :param Document doc: PyLatex document handler.
        :return None: None
        """

        # Start writing.
        doc.append(NoEscape(r"\section{\sc Employment}"))
        companies = unique([sub["employer"] for sub in listify(self.resume_data.get_achievements())])
        for employer in companies:
            employer_name = self.resume_data.query_name(employer, "employer")
            doc.append(bold(employer_name))
            doc.append(NewLine())
            for position in listify(self.resume_data.get_positions()):
                if employer == position["employer"]:
                    position_name = self.resume_data.query_name(position["position"], "position")
                    end_date = "Present" if self.cmd.format_date(
                        position["enddate"]) == "" else self.cmd.format_date(position["enddate"])
                    doc.append(NoEscape(
                        r"{\em "
                        + position_name
                        + r"} \hfill {"
                        + r"\textbf {"
                        + self.cmd.format_date(position["startdate"])
                        + r" {--} "
                        + f"{end_date}"
                        + r"}}"))
                    doc.append(NoEscape(r"\begin{list2}"))
                    for achievement in listify(self.resume_data.get_achievements()):
                        if employer == achievement["employer"] and position["position"] == achievement["position"]:
                            doc.append(NoEscape(
                                r"\item " + self.cmd.glossary_inject(achievement["longdesc"], "retro")))
                    doc.append(NoEscape(r"\end{list2}"))

    @staticmethod
    def count_instances(instance_list: list[str | bool], x: any) -> int:
        """
        Count the number of times a list element shows up.
        :param list[str | bool] instance_list:
        :param any x:
        :return int: Match count.
        """

        count_int = 0
        for element in instance_list:
            if element == x:
                count_int = count_int + 1
        return count_int
