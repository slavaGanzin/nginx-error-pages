import requests
from pathlib import Path

Path("error-pages/").mkdir(exist_ok=True)

r = requests.get("http://webconcepts.info/concepts/http-status-code.json")
json = r.json()

css = open("_errors/main.css", "r").read()
for i in json["values"]:
    template = "templates/" + i["value"][0:1] + "xx.html"
    with open(template) as f:
        content = f.read().replace(
            r"""<link rel="stylesheet" type="text/css" href="/_errors/main.css"/>""",
            "<style>" + css + "</style>",
        )
        new_content = content
        error_code = int(i["value"])

        print("Error Code: %d" % (error_code))

        if error_code == 418 or error_code < 400 or error_code > 599:
            continue
        new_content = new_content.replace("$ERROR_CODE", i["value"])
        new_content = new_content.replace("$ERROR_NAME", i["description"])
        new_content = new_content.replace("$ERROR_DESC", i["details"][0]["description"])
        with open("error-pages/" + i["value"] + ".html", "w") as output_file:
            output_file.write(new_content)

with open("error-pages/error-pages.conf", "w") as epc:
    for i in json["values"]:
        v = int(i["value"])
        if v < 400 or v > 599:
            continue
        print("error_page %d /error-pages/%d.html;" % (v, v), file=epc)
    print(
        """
location ~ /error-pages/(10[0-3]|2[02][1-9]|30[1-8]|4[0125][0-9]|50[0-9])\.html {
    sub_filter '%{HOSTNAME}' $host;
    sub_filter_once off;
    allow all;
    internal;
}
""",
        file=epc,
    )
