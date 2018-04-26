#! /usr/bin/env python3

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER


styles = getSampleStyleSheet()

styles.add(ParagraphStyle(name='Justify',
                          fontName='Times-Roman',
                          alignment=TA_JUSTIFY,
                          firstLineIndent=25,
                          fontSize=14,
                          leading=17))

styles.add(ParagraphStyle(name='Announcement',
                          fontName='Times-Bold',
                          alignment=TA_CENTER,
                          fontSize=16,
                          leading=22))

styles.add(ParagraphStyle(name='TitleBig',
                          fontName='Times-Bold',
                          alignment=TA_CENTER,
                          fontSize=14,
                          leading=22))

styles.add(ParagraphStyle(name='SubTitleBig',
                          fontName='Times-Bold',
                          alignment=TA_CENTER,
                          fontSize=14,
                          leading=18))

styles.add(ParagraphStyle(name='AuthorBig',
                          fontName='Times-Bold',
                          alignment=TA_CENTER,
                          fontSize=12,
                          leading=14))

styles.add(ParagraphStyle(name='Citation',
                          fontName='Times-Roman',
                          alignment=TA_JUSTIFY,
                          firstLineIndent=0,
                          fontSize=14,
                          leading=17))
