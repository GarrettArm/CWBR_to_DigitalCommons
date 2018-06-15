#!/usr/bin/env python3

import csv
import os
from collections import namedtuple
import string

from nameparser import HumanName


def csv_to_dict(filename):
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


def make_paragraphs_text(issue):
    return '\n\t'.join([i for i in
                        issue.Review.replace('<br>', '<p>')
                                    .replace('</br>', '</p>')
                                    .replace('</p>', '')
                                    .split('<p>')
                        if i])


def make_announcement_block(issue):
    record_type = issue.Record_type
    if record_type.lower() == 'classics':
        return 'Feature Essay'
    elif record_type.lower() in ('interview', 'editorial', 'review', ):
        return record_type


def format_title_parts(string_segment):
    string_segment = string.capwords(string_segment, ' ')
    string_segment = string_segment.lstrip().replace("'S ", "'s ").replace('’', "'")
    string_segment = string_segment.replace('“', '"')
    string_segment = string_segment.replace('</p>', '').replace('<p>', '')
    return string_segment


def make_title_block(issue):
    title_parts, subtitle_parts = find_title_lines(issue)
    title_string = ''.join([format_title_parts(title_part)
                            for title_part in title_parts if title_part])
    subtitle_string = ''.join([format_title_parts(subtitle_part)
                               for subtitle_part in subtitle_parts if subtitle_part])
    if title_string and subtitle_string:
        return ': '.join([title_string, subtitle_string])
    else:
        return ''.join([title_string, subtitle_string])


def pull_title_from_Title(issue):
        title = strip_bolds_breaks(issue.Title).replace('EDITORIAL:', '').replace('INTERVIEW:', '')
        title_parts = [item for item in title.split('<p>') if item]
        subtitle_parts = ''
        return title_parts, subtitle_parts


def pull_title_from_Headline(issue):
        title_parts = [item for item in issue.Headline.split('<p>') if item]
        subtitle_parts = [item for item in issue.Sub_headline.split('<p>') if item]
        return title_parts, subtitle_parts


def find_title_lines(issue):
    if issue.Record_type not in ('Editorial', 'Interview'):
        title_parts, subtitle_parts = pull_title_from_Headline(issue)
    else:
        title_parts, subtitle_parts = pull_title_from_Title(issue)
    if not (title_parts or subtitle_parts):
        title_parts, subtitle_parts = pull_title_from_Title(issue)
    return title_parts, subtitle_parts


def strip_bolds_breaks(text):
    for i in ('<br>', '</br>', '<BR>', '</BR>', '<b>', '</b>', '<B>', '</B>', ):
        text = text.replace(i, '')
    return text


def pick_authors(issue):
    author_list = []
    if issue.Record_type not in ('Review', 'Classics'):
        for author in (issue.Auth_1, issue.Auth_2, issue.Auth_3):
            if author:
                author = author.replace('<br>', '<p>').replace('</br>', '</p>')
                author_list.append(author)
        return author_list
    else:
        if issue.Reviewer:
            author_list.append(issue.Reviewer)
        return author_list


def parse_name(name):
    parsed_name = HumanName(name)
    first = parsed_name.first
    middle = parsed_name.middle
    last = parsed_name.last
    suffix = parsed_name.suffix
    return (first, middle, last, suffix)


def reformat_issue_type(issue_type):
    internal_external_dict = {'Editorial': 'editorial',
                              'Classics': 'feature_essay',
                              'Interview': 'author_interview',
                              'Review': 'review',
                              }
    return internal_external_dict[issue_type]


def make_publication_date(issue_date):
    season, year = issue_date.split(' ')

    seasons_month_dict = {'Spring': '03',
                          'Summer': '06',
                          'Fall': '09',
                          'Winter': '12'}
    month = seasons_month_dict[season]
    return '{}-{}-01'.format(year, month)


def make_season(issue_date):
    return issue_date.split(' ')[0]


def make_url(issue_id):
    return 'https://s3-us-west-2.amazonaws.com/cwbr-publicshare/{}.pdf'.format(issue_id)


def make_csv_data(issues_dict):
    csv_data = []
    csv_data.append(['title',
                     'book_id',
                     'fulltext_url',
                     'isbn',
                     'price',
                     'publication_date',
                     'season',
                     'document_type',
                     'publisher',
                     'book_pub_date',
                     'author1_fname',
                     'author1_mname',
                     'author1_lname',
                     'author1_suffix',
                     'author2_fname',
                     'author2_mname',
                     'author2_lname',
                     'author2_suffix',
                     'author3_fname',
                     'author3_mname',
                     'author3_lname',
                     'author3_suffix',
                     'abstract',
                     ])
    for k, issue in sorted(issues_dict.items()):
        authors_list = pick_authors(issue)
        author1_fname, author1_mname, author1_lname, author1_suffix = '', '', '', ''
        author2_fname, author2_mname, author2_lname, author2_suffix = '', '', '', ''
        author3_fname, author3_mname, author3_lname, author3_suffix = '', '', '', ''
        if authors_list:
            author1_fname, author1_mname, author1_lname, author1_suffix = parse_name(authors_list[0])
        if len(authors_list) > 1:
            author2_fname, author2_mname, author2_lname, author2_suffix = parse_name(authors_list[1])
        if len(authors_list) > 2:
            author3_fname, author3_mname, author3_lname, author3_suffix = parse_name(authors_list[2])
        csv_data.append([make_title_block(issue),
                         issue.ID,
                         make_url(issue.ID),
                         issue.ISBN,
                         issue.Price,
                         make_publication_date(issue.Issue_date),
                         make_season(issue.Issue_date),
                         reformat_issue_type(issue.Record_type),
                         issue.Publisher,
                         issue.Pub_date,
                         author1_fname,
                         author1_mname,
                         author1_lname,
                         author1_suffix,
                         author2_fname,
                         author2_mname,
                         author2_lname,
                         author2_suffix,
                         author3_fname,
                         author3_mname,
                         author3_lname,
                         author3_suffix,
                         make_paragraphs_text(issue),
                         ])
    csv_writer(csv_data)


def csv_writer(data):
    output_dir = 'uploadSpreadsheet'
    os.makedirs(output_dir, exist_ok=True)

    with open('uploadSpreadsheet/DigitalCommonsSpreadsheet.csv', "w", newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter='\t', quotechar='"')
        for line in data:
            writer.writerow(line)


if __name__ == '__main__':
    issues_dict = csv_to_dict('3rdStageSourceCSVs/Interviews.csv')
    make_csv_data(issues_dict)
