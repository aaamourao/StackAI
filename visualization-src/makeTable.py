#!/usr/bin/env python2

from userTable import UserTable

if __name__ == '__main__':
  UserTable('../stackexchange').saveTable('full_table.csv')
