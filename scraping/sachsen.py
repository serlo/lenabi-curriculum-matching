from lxml import html
import json
import sys

def parseHTML(fobj):

    f = fobj.read()

    root = html.fromstring(f)

    tree = {"name": "Lehrplan", "children": []}
    for page in root.xpath("//div[@class=\"lplanpage\"]"):
        if "stufe" in page.get("data-ci"):

            pagenode = {"name": page.get("data-ci"), "children": []}
            tree["children"].append(pagenode)
            #lernbereich
            for lb in page.xpath("./div/div[@class=\"lernbereich\"]"):
                lbnode = {"name": lb.get("data-ci"), "children": []}
                pagenode["children"].append(lbnode)

                layerchildren = {1: [], 2: [], 3: []}

                last_layer = 1
                for lz in lb.xpath("./div/table/tr/td[@class=\"lz\"]"):
                    text = lz.xpath("string()")
                    layer = 0
                    for cls in lz.getparent().get("class").split(" "):
                        cls = cls.strip()
                        if cls.startswith("lze"):
                            layer = int(cls[3:])
                            assert layer in [1, 2, 3]
                            break
                    else:
                        assert ValueError("could not determine layer.")

                    if last_layer == layer:
                        layerchildren[layer].append({"text": text, "children": []})
                    elif last_layer < layer:
                        layerchildren[layer].append({"text": text, "children": []})
                        for sub in range(layer + 1, 3 + 1):
                            layerchildren[sub] = []

                    while last_layer > layer:
                        layerchildren[last_layer - 1][-1]["children"] = layerchildren[last_layer]
                        layerchildren[last_layer] = []
                        last_layer -= 1;

                    last_layer = layer
                lbnode["children"] = layerchildren[1]
    return tree

def print_tree(t, depth = 0):
    print (" " * depth, t.get("name") if "name" in t else t.get("text"), file=sys.stderr)
    for c in t["children"]:
        print_tree(c, depth + 1)

if __name__ == "__main__":
    tree = parseHTML(sys.stdin)
    #print_tree(tree)
    json.dump(tree, sys.stdout)
