# Ben Levi 318811304 and Eliran Eiluz 313268146

import requests
from lxml import etree
import time
import heapq


# This class is used as the priority queue of the crawler.
class CrawlerPriorityQueue:

    def __init__(self):
        self.links = []

    # we add a new link to the heap as a tuple (link_priority, link).
    # python heap automatically sorts the node according to the first element in the tuple.
    # we use time to break ties.
    def add_link(self, link, descendants_set, index):
        if not self.is_in_queue(link):
            heapq.heappush(self.links, (len(descendants_set), index, link, descendants_set))

    # extract the minimum out of the heap and return the second element in the tuple,
    # which is the node object. If heap is empty, raise an exception.
    def extract_min(self):
        if self.links:
            return heapq.heappop(self.links)[2]
        else:
            return None

    # This method is used to update a link when we discover a new descendant of him.
    def update_link(self, link, new_descendant):
        if self.is_in_queue(link):
            link_time, descendant_set = self.delete_link(link)
            descendant_set.add(new_descendant)
            self.add_link(link, descendant_set, link_time)

    # This method is used in the update_link method. To update a link, we delete him, heapify the heap and re-enter
    # him with its new priority.
    def delete_link(self, link):
        for li in self.links:
            if li[2] == link:
                self.links.remove(li)
                heapq.heapify(self.links)
                return li[1], li[3]
        return None, None

    # This method is used to check whether a link is in the queue.
    # If yes, return the url. If not, return None.
    def is_in_queue(self, link):
        for li in self.links:
            if li[2] == link:
                return li
        return None

    def is_empty(self):
        return len(self.links) == 0


def britishCrawler(url, verifyXpath, descendantXpaths, ancestorXpaths, royaltyXpaths):
    # As stated in the exersice, the maximum amount of crawls is 30.
    MAX_AMOUNT_OF_CRAWLS = 30

    # Current amount of crawls. Starting from 0.
    amount_of_crawls = 0

    # The index is used as a tie-breaker for the priority queue in case two(or more) links have the same amount of
    # descendants. We increase it each time we insert a new link to the queue.
    index = 0

    # a dictionary that maps between a url to a list that contains lists in this format:
    # [this_url, discovered_url, is_crawled].
    # this_url - the key url.
    # discovered_url - a url that has been discovered by crawling the key url.
    # is_crawled - 0/1 value that indicates if we crawled on discovered_url or not.
    links_dict = dict()

    # Create an instance of the queue, add the start link to the queue and increase
    links_heap = CrawlerPriorityQueue()
    links_heap.add_link(url, set(), index)
    index += 1

    # Keep crawling as long as the heap is not empty.
    # We have this condition because the queue may be empty before we passed the amount of crawls.
    # (like, in case we started crawling from a "bad" url)
    while not links_heap.is_empty():

        # Extract the minimum from the heap.
        link = links_heap.extract_min()

        # Check if we already crawled on this url. If yes, continue.
        if link in links_dict.keys():
            continue

        # Increase the amount of crawls and check whether we passed the limit. if yes, break.
        amount_of_crawls += 1
        if amount_of_crawls > MAX_AMOUNT_OF_CRAWLS:
            break

        # Download the page content and make it a tree.
        page = requests.get(link)
        html = etree.HTML(page.content)

        # If the verifyXpath is not empty or null, check if the page passes the verification.
        # If no, delete any pair that this link appears in it's left side, sleep 3 seconds and continue to another link.
        if verifyXpath is not None and verifyXpath != "":
            if len([u for u in html.xpath(verifyXpath)]) == 0:
                for value in links_dict.values():
                    for lst in value:
                        if lst[1] == link:
                            value.remove(lst)
                time.sleep(3)
                continue

        # Change is_crawled value to any pair that this links appears in it's left side to 1.
        # That is because we are crawling on this link.
        for value in links_dict.values():
            for lst in value:
                if lst[1] == link:
                    lst[2] = 1

        # add the link that we are crawling on to the dictionary and create an empty list of pairs for him.
        links_dict[link] = ([])

        # extract links from the page we are crawling on for each category(if not empty):
        # descendant, ancestor and royalty.
        links_from_descendant = set()
        if descendantXpaths is not None:
            for query in descendantXpaths:
                for u in html.xpath(query):
                    if not str(u).startswith("https"):
                        u = "https://www.wikipedia.org" + u
                    links_from_descendant.add(u)
        links_from_ancestor = set()
        if ancestorXpaths is not None:
            for query in ancestorXpaths:
                for u in html.xpath(query):
                    if not str(u).startswith("https"):
                        u = "https://www.wikipedia.org" + u
                    links_from_ancestor.add(u)

        # With the ancestor links we can discover whether a link that appears in the queue
        # have descendants that we didn't know about yet and update its priority accordingly.
        for li in links_from_ancestor:
            if links_heap.is_in_queue(li):
                links_heap.update_link(li, link)

        links_from_royalty = set()
        if royaltyXpaths is not None:
            for query in royaltyXpaths:
                for u in html.xpath(query):
                    if not str(u).startswith("https"):
                        u = "https://www.wikipedia.org" + u
                    links_from_royalty.add(u)

        # union all the discovered links to a set, sort it(for the determinism of the crawler),
        # and add each link to the queue.
        all_links = links_from_descendant.union(links_from_ancestor).union(links_from_royalty)
        all_links = sorted(all_links)
        for li in all_links:
            links_heap.add_link(li, set(), index)
            index += 1
            links_dict[link].append([str(link), str(li), 0])

        # sleep 3 seconds before the next crawl, as stated in the exercise.
        time.sleep(3)

    # When the crawling finishes, union all the list of pairs of all the crawled links to one list,
    # and return it as the output of the crawler.
    links_list = []
    for lst in links_dict.values():
        links_list += lst
    return links_list

# If you wish to use the crawler with our Xpaths, you may use this main, as the lists contains our Xpaths.
# if __name__ == '__main__':
#     list_of_pairs = britishCrawler("https://en.wikipedia.org/wiki/Charles_III",
#                                    "//table[contains(@class,'sidebar') or contains(@class,'infobox')]//a[contains(text(),'Windsor') or contains(@title,'British royal family')]",
#                                    [
#                                        "//*[(contains(@class,'infobox-label') and text()='Issue')]/..//a[starts-with(@href,'/wiki/') or starts-with(@href,'https://en.wikipedia.org')]/@href"],
#                                    [
#                                        "//*[(contains(@class,'infobox-label') and (text()='Father' or text()='Mother'))]/..//a[starts-with(@href,'/wiki/') or starts-with(@href,'https://en.wikipedia.org')]/@href"
#                                    ],
#                                    []
#                                    )
