#! /usr/bin/env python3

import os
import csv
from collections import namedtuple

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from styles_CWBR import styles


def parse_csvs():
    issues_dict = dict()
    for filename in ('3rdStageSourceCSVs/Interviews.csv', ):
        file_dict = csv_to_namedtuple(filename)
        issues_dict.update(file_dict)
    return issues_dict


def csv_to_namedtuple(filename):
    file_dict = dict()
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='\t', quotechar='"')
        headers = next(csvreader)
        CWBR = namedtuple('CWBR', headers)
        for row in csvreader:
            item = CWBR(*row)
            if file_dict.get(item.ID):
                print('**** Two examples of {} in these spreadsheets ****'.format(item.ID))
                exit()
            file_dict[item.ID] = item
    return file_dict


def do_annotation_types(issues_dict):
    seasons_annoItems = group_all_annotations_by_season(issues_dict)
    for season, annoItems in sorted(seasons_annoItems.items()):
        print(season)
        do_an_annotation_season(season, annoItems)


def group_all_annotations_by_season(issues_dict):
    all_annotations_by_season = dict()
    for k, v in issues_dict.items():
        if v.Record_type.lower().strip() == 'annotation':
            if v.Issue_date in all_annotations_by_season:
                all_annotations_by_season[v.Issue_date].append(v)
            else:
                all_annotations_by_season[v.Issue_date] = [v, ]
    return all_annotations_by_season


def do_an_annotation_season(filename, annoItems):
    annoItems = sorted(annoItems, key=(lambda x: x.Title))
    template = []
    template += [Paragraph('ANNOTATIONS', styles['Announcement']), ]
    template += [Spacer(1, 0.1 * inch)]
    for annoItem in annoItems:
        template += make_annotation_template(annoItem)
    filename = filename.replace('/', '_').replace(' ', '')
    write_pdf(filename, template)


def make_annotation_template(issue):
    template = []
    template += make_title_block(issue)
    template += [Spacer(1, 0.1 * inch)]
    template += make_author_block(issue)
    template += [Spacer(1, 0.05 * inch)]
    template += [Paragraph(issue.Issue_date, styles['AuthorBig'])]
    template += [Spacer(1, 0.5 * inch)]
    if issue.Record_type != 'Editorial':
        template += make_citation_block(issue)
        template += [Spacer(1, 0.2 * inch)]
    template += make_paragraph_block(issue)
    return template


def do_normal_pdfs(issues_dict):
    for uri, issue_namedtuple in issues_dict.items():
        if issue_namedtuple.Record_type.lower() == "annotation":
            continue
        if not os.path.isfile('good_pdfs/{}.pdf'.format(uri)):
            print("*** STARTING: {} ***".format(issue_namedtuple.ID))
            template = make_normal_template(issue_namedtuple)
            write_pdf(issue_namedtuple.ID, template)


def make_normal_template(issue):
    template = []
    template += make_announcement_block(issue)
    template += [Spacer(1, 0.1 * inch)]
    template += make_title_block(issue)
    template += [Spacer(1, 0.1 * inch)]
    template += make_author_block(issue)
    template += [Spacer(1, 0.1 * inch)]
    template += [Paragraph(issue.Issue_date, styles['AuthorBig'])]
    template += [Spacer(1, 0.5 * inch)]
    if issue.Record_type != 'Editorial':
        template += make_citation_block(issue)
        template += [Spacer(1, 0.4 * inch)]
    template += make_paragraph_block(issue)
    return template


def make_announcement_block(issue):
    announcement_block = []
    record_type = issue.Record_type
    if record_type.lower() == 'classics':
        p = Paragraph('Feature Essay', styles['Announcement'])
        announcement_block.append(p)
    elif record_type.lower() in ('interview', 'editorial', 'review', ):
        p = Paragraph(record_type, styles['Announcement'])
        announcement_block.append(p)
    return announcement_block


def make_title_block(issue):
    title_block = []
    title_parts, subtitle_parts = find_title_lines(issue)
    if title_parts:
        title_block.extend([Paragraph(title_part.upper(), styles['TitleBig'])
                            for title_part in title_parts])
    if subtitle_parts:
        title_block.extend([Paragraph(subtitle_part, styles['SubTitleBig'])
                            for subtitle_part in subtitle_parts])
    return title_block


def find_title_lines(issue):
    if issue.Record_type in ('Editorial', 'Interview', ):
        title = strip_bolds_breaks(issue.Title).replace('EDITORIAL:', '').replace('INTERVIEW:', '')
        title_parts = [item for item in title.split('<p>') if item]
        subtitle_parts = None
        return title_parts, subtitle_parts
    else:
        title_parts = [item for item in issue.Headline.split('<p>') if item]
        subtitle_parts = [item for item in issue.Sub_headline.split('<p>') if item]
        return title_parts, subtitle_parts


def strip_bolds_breaks(text):
    for i in ('<br>', '</br>', '<BR>', '</BR>', '<b>', '</b>', '<B>', '</B>', ):
        text = text.replace(i, '')
    return text


def make_author_block(issue):
    author_block = []
    if issue.Record_type not in ('Review', 'Classics'):
        for author in (issue.Auth_1, issue.Auth_2, issue.Auth_3):
            if author:
                author = author.replace('<br>', '<p>').replace('</br>', '</p>')
                p = Paragraph(author, styles['AuthorBig'])
                author_block.append(p)
    else:
        if issue.Reviewer:
            p = Paragraph(issue.Reviewer, styles['AuthorBig'])
            author_block.append(p)
    return author_block


def make_citation_block(issue):
    citation_block = []
    authors_list = [i for i in (issue.Auth_1, issue.Auth_2, issue.Auth_3) if i]
    if len(authors_list) == 1:
        authors = '<b>{}</b> '.format(authors_list[0])
    elif len(authors_list) == 2:
        authors = '<b>{} and {}.</b> '.format(authors_list[0], authors_list[1])
    elif len(authors_list) == 3:
        authors = '<b>{}, {}, and {}.</b> '.format(authors_list[0], authors_list[1], authors_list[2])
    else:
        authors = ''

    book_title = '<i>{}.</i> '.format(strip_paragraphs_breaks(issue.Title))

    if issue.Publisher:
        publisher = '{}, '.format(issue.Publisher)
    else:
        publisher = ''
    if issue.Pub_date:
        pub_date = '{}. '.format(issue.Pub_date)
    else:
        pub_date = ''
    citation = '{}{}{}{}{} '.format(authors,
                                    strip_paragraphs_breaks(book_title),
                                    publisher,
                                    pub_date,
                                    strip_paragraphs_breaks(issue.Price),
                                    )
    if issue.ISBN:
        citation += 'ISBN {}'.format(strip_paragraphs_breaks(issue.ISBN))
    if issue.Record_type not in ('Interview', ):

        p = Paragraph(citation, styles['Citation'])
        citation_block.append(p)
    return citation_block


def strip_paragraphs_breaks(text):
    for i in ('<br>', '</br>', '<p>', '</p>', '<BR>', '</BR>', ):
        text = text.replace(i, '')
    return text


def make_paragraph_block(issue):
    paragraph_block = []
    list_of_paragraphs = [i for i in
                          issue.Review.replace('<br>', '<p>').replace('</br>', '</p>').split('<p>')
                          if i]
    for item in list_of_paragraphs:
        p = Paragraph(item, styles['Justify'])
        paragraph_block.append(p)
        paragraph_block.append(Spacer(1, 0.2 * inch))
    return paragraph_block


def write_pdf(filename, template):
    doc = SimpleDocTemplate('output/{}.pdf'.format(filename),
                            pagesize=letter,
                            rightMargin=72,
                            leftMargin=72,
                            topMargin=72,
                            bottomMargin=50
                            )
    doc.build(template)


if __name__ == '__main__':
    os.makedirs('output', exist_ok=True)
    os.makedirs('good_pdfs', exist_ok=True)
    issues_dict = parse_csvs()

    do_annotation_types(issues_dict)
    do_normal_pdfs(issues_dict)
