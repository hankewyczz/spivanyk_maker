from typing import List, Union

import requests

API_URL = "https://www.wikispiv.com/api.php?format=json"


def title_search(name: str) -> Union[str, None]:
    '''
    Finds the title most closely matching the given title
    :param name: The name for which we want to search
    :return: Either the closest matching name, or None if no titles match closely enough
    '''
    name = name.replace("_", " ")
    response = requests.get(f"{API_URL}&action=query&list=search&srsearch={name}").json()
    results = response["query"]["search"]

    if len(results) > 0:
        return results[0]["title"]

    return None



def get_root_page(name: str) -> str:
    '''
    Gets the root page - ie. the page to which this page redirects to.
    :param name: The EXACT name of the page we want to query
    :return: the title of the root page
    '''
    response = requests.get(f"{API_URL}&action=query&titles={name}&redirects").json()
    # Get the resulting page from this query. This is the root page - ie. follow all redirects until there are no more
    #   If a page has no redirects, the root page is itself
    main_pages = response["query"]["pages"].values()
    main_page = list(main_pages)[0]

    if "missing" in main_page:
        new_name = title_search(name)
        if new_name:
            return get_root_page(new_name)

        raise ValueError(f"No song matching {name} found")

    return main_page["title"]

def get_backlinks(name: str) -> List[str]:
    '''
    Find every page which redirects to this page
    :param name: The EXACT name of the page, for which we want to find the backlinks
    :return: The titles of every page which redirects to this one
    '''
    response = requests.get(f"{API_URL}&action=query&list=backlinks&bltitle={title_search(name)}").json()
    return [link["title"] for link in response["query"]["backlinks"]]

def get_alternate_titles(name: str) -> List[str]:
    '''
    Gets all alternate titles of this song
    :param name: The EXACT name of the song for which we want all the alternate titles
    :return: A list of all titles
    '''
    name = title_search(name)

    if not name:
        return []

    root_name = get_root_page(name)
    names = get_backlinks(root_name)
    names.append(root_name)
    return [n for n in names if n != name]


def main():
    print(get_root_page("Цвіт України і краса"))
    print(get_root_page("Гімн Пласту"))
    print(get_root_page("Пластовий гімн"))

    print(get_alternate_titles("Цвіт України і краса"))
    print(get_alternate_titles("Гімн Пласту"))
    print(get_alternate_titles("Пластовий гімн"))


if __name__ == '__main__':
    main()