import posixpath
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from book_tools.paths import output_path, write_text


def archive_path(base, reference):
    path = posixpath.normpath(posixpath.join(posixpath.dirname(base), unquote(urlsplit(reference).path)))
    if path.startswith(("/", "../")) or path == "..":
        raise ValueError(f"Invalid EPUB resource path: {reference}")
    return path


def epub_to_markdown(input_path, output=None):
    from bs4 import BeautifulSoup
    from markdownify import MarkdownConverter

    class BookConverter(MarkdownConverter):
        def convert_a(self, element, text, parent_tags):
            anchor = f'<a id="{element["id"]}"></a>' if element.get("id") else ""
            return anchor + super().convert_a(element, text, parent_tags)

    destination = output_path(input_path, output)
    try:
        with ZipFile(input_path) as archive:
            container = ElementTree.fromstring(archive.read("META-INF/container.xml"))
            rootfile = container.find(".//{*}rootfile")
            if rootfile is None or not rootfile.get("full-path"):
                raise ValueError("EPUB has no package document")
            package_path = archive_path("", rootfile.attrib["full-path"])
            package = ElementTree.fromstring(archive.read(package_path))
            manifest = {item.attrib["id"]: item for item in package.findall("./{*}manifest/{*}item")}
            chapters = []
            for reference in package.findall("./{*}spine/{*}itemref"):
                if reference.get("linear", "yes") == "no":
                    continue
                item = manifest[reference.attrib["idref"]]
                if item.get("media-type") not in {"application/xhtml+xml", "text/html"}:
                    raise ValueError("EPUB contains an unsupported chapter format")
                chapters.append(archive_path(package_path, item.attrib["href"]))
            if not chapters:
                raise ValueError("EPUB contains no readable chapters")
            if "META-INF/encryption.xml" in archive.namelist():
                encryption = ElementTree.fromstring(archive.read("META-INF/encryption.xml"))
                for encrypted in encryption.findall(".//{*}EncryptedData"):
                    method = encrypted.find("./{*}EncryptionMethod")
                    algorithm = method.get("Algorithm", "") if method is not None else ""
                    if algorithm not in {"http://www.idpf.org/2008/embedding", "http://ns.adobe.com/pdf/enc#RC"}:
                        raise ValueError("DRM-protected EPUBs are not supported")
            documents = [(chapter, BeautifulSoup(archive.read(chapter), "html.parser")) for chapter in chapters]
            anchors = {}
            for index, (chapter, soup) in enumerate(documents, 1):
                anchors[(chapter, "")] = f"chapter-{index}"
                for anchor_index, element in enumerate(soup.find_all(attrs={"id": True}), 1):
                    anchors[(chapter, element["id"])] = f"chapter-{index}-anchor-{anchor_index}"
            parts = []
            images = {}
            converter = BookConverter(heading_style="ATX", bullets="-", keep_inline_images_in=["h1", "h2", "h3", "td"])
            for chapter, soup in documents:
                for unwanted in soup.find_all(["head", "script", "style"]):
                    unwanted.decompose()
                for element in list(soup.find_all(attrs={"id": True})):
                    anchor = soup.new_tag("a", id=anchors[(chapter, element["id"])])
                    del element["id"]
                    element.insert_before(anchor)
                for image in soup.find_all("img"):
                    source = image.get("src", "")
                    parsed = urlsplit(source)
                    if not source or parsed.scheme or parsed.netloc:
                        continue
                    resource = archive_path(chapter, source)
                    if resource not in images:
                        suffix = Path(resource).suffix or ".bin"
                        relative = f"{destination.stem}.images/image-{len(images) + 1}{suffix}"
                        images[resource] = (relative, archive.read(resource))
                    image["src"] = quote(images[resource][0], safe="/")
                for link in soup.find_all("a", href=True):
                    parsed = urlsplit(link["href"])
                    if not parsed.scheme and not parsed.netloc:
                        target = archive_path(chapter, link["href"]) if parsed.path else chapter
                        anchor = anchors.get((target, unquote(parsed.fragment)))
                        if anchor:
                            link["href"] = f"#{anchor}"
                markdown = converter.convert_soup(soup)
                parts.append(f'<a id="{anchors[(chapter, "")]}"></a>\n\n{markdown.strip()}')
            for relative, data in images.values():
                image_path = destination.parent / relative
                image_path.parent.mkdir(parents=True, exist_ok=True)
                image_path.write_bytes(data)
            return write_text(destination, "\n\n".join(parts) + "\n")
    except (BadZipFile, KeyError, ElementTree.ParseError) as error:
        raise ValueError(f"Malformed or incomplete EPUB: {error}") from error
