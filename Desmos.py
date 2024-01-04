import datetime
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

print("start " + str(datetime.datetime.now()))

option = Options()
option.add_experimental_option("detach", True)
option.add_argument("--start-maximized")

driver = webdriver.Chrome(options=option)

URL = "https://www.desmos.com/calculator"
driver.get(URL)
print("driver open " + str(datetime.datetime.now()))
filePath = ""
multibleFiles = bool(True)


def Desmos(svg, color):
    paths = svg.split('<path d="')
    paths.pop(0)
    paths[-1] = paths[-1].split("</g>")
    paths.pop(-1)

    svg = "".join(paths)

    splits = ["M", "c", "C", "l", "m"]
    svg = svg.replace("\n", " ")

    svg = svg.replace('<path d="', '')
    svg = svg.replace('z"/>', '')
    svg = svg.replace('z', '')

    for split in splits:
        test = "å" + split
        svg = test.join(svg.split(split))
        svg.join(svg)

    Divs = svg.split(" å")
    x = 0
    y = 0
    latexes = []
    for div in Divs:
        if "M" in div:
            div = div.replace('M', "")
            div = div.replace('å', "")

            x, y = div.split(" ", 1)
            x = int(x)
            y = int(y)
        elif "m" in div:
            div = div.replace('m', "")

            xc, yc = div.split(" ", 1)
            x += int(xc)
            y += int(yc)
        elif "l" in div:
            div = div.replace('l', "")
            numbers = div.split(" ")
            isx = True
            p2x = x
            p2y = y
            for number in numbers:
                if number == '':
                    continue
                if isx:
                    x += int(number)
                else:
                    y += int(number)
                    p1x = p2x
                    p1y = p2y
                    p2x = x
                    p2y = y
                    latexX = str(p1x) + "+ t(" + str(p2x) + "-" + str(p1x) + ")"
                    latexY = str(p1y) + "+ t(" + str(p2y) + "-" + str(p1y) + ")"
                    latex = "((" + latexX + "), (" + latexY + "))"
                    latexes.append(latex)

                isx = not isx
        elif "c" in div:
            div = div.replace('c', "")
            numbers = div.split(" ")
            isx = True
            pointSet = 1
            p4x = x
            p4y = y
            for number in numbers:
                if number == '':
                    continue
                if isx:
                    if pointSet == 1:
                        p1x = p4x
                        p2x = p1x + int(number)
                    elif pointSet == 2:
                        p3x = p1x + int(number)
                    elif pointSet == 3:
                        p4x = p1x + int(number)
                        x = p4x
                else:
                    if pointSet == 1:
                        p1y = p4y
                        p2y = p1y + int(number)
                    elif pointSet == 2:
                        p3y = p1y + int(number)
                    elif pointSet == 3:
                        p4y = p1y + int(number)
                        y = p4y
                        latexX = "(1-t)^3 " + str(p1x) + " + 3t(1-t)^2 " + str(p2x) + " + 3t^2 (1-t) " + str(
                            p3x) + " + t^3 " + str(p4x)
                        latexY = "(1-t)^3 " + str(p1y) + " + 3t(1-t)^2 " + str(p2y) + " + 3t^2 (1-t) " + str(
                            p3y) + " + t^3 " + str(p4y)
                        latex = "((" + latexX + "), (" + latexY + "))"
                        latexes.append(latex)
                        pointSet = 0
                    pointSet += 1
                isx = not isx
        else:
            print("undefined" + div)

    print("Latex Done " + str(datetime.datetime.now()))
    calc_strings = []
    for lat in latexes:
        calc_strings.append('Calc.setExpression({latex: "' + lat + '", color: "' + color + '"});')
    print("js Commands generated " + str(datetime.datetime.now()))
    for calc_string in calc_strings:
        driver.execute_script(calc_string)
    print("All done " + str(datetime.datetime.now()))


def MoreFiles():
    print("Use multiple File (Y/N)")
    inpat = input()
    if inpat.lower() == "y":
        return True
    elif inpat.lower() == "n":
        return False
    else:
        print("Not a valid answer")
        MoreFiles()

def FileInput():
    multibleFiles = MoreFiles()
    print("Input file path:")
    filePath = str(input())
    if os.path.exists(filePath):
        if multibleFiles == True:
            print("Input Color hex:")
            color = str(input())
            i = 0
            try:
                os.makedirs(filePath + "/pictures")
            except FileExistsError:
                pass

            for fil in os.listdir(filePath):
                print(fil)
                i += 1
                try:
                    file = open(filePath + '/' + fil, "r")
                    svg = file.read()
                    file.close()
                    Desmos(svg, color)

                    driver.execute_script("Calc.setViewport([0,8000,0,5793])")
                    driver.forward()

                    driver.save_screenshot(filePath + '/pictures/Picture' + str(i) + '.png')
                    driver.execute_script("Calc.setBlank()")

                except OSError:
                    print("Not valid file path")
                    FileInput()
        else:
            try:
                file = open(filePath, "r")
                svg = file.read()
                file.close()
                print("Input Color hex:")
                color = str(input())
                Desmos(svg, color)

            except OSError:
                print("Not valid file path")
                FileInput()
    else:
        print("Invalid file path")
        FileInput()


FileInput()
