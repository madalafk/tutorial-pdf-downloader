import random
import time

class NANDCell:
    def __init__(self):
        self.state = 0  # 0 represents an erased cell, 1 represents a written cell

class NANDPage:
    def __init__(self, page_size):
        self.cells = [NANDCell() for _ in range(page_size)]
        self.valid_data = False  # To simulate whether the data in this page is valid or not

class NANDBlock:
    def __init__(self, page_size, pages_per_block):
        self.pages = [NANDPage(page_size) for _ in range(pages_per_block)]
        self.erased = True

class SSD:
    def __init__(self, block_count, page_size, pages_per_block, read_speed, write_speed):
        self.blocks = [NANDBlock(page_size, pages_per_block) for _ in range(block_count)]
        self.block_count = block_count
        self.page_size = page_size
        self.pages_per_block = pages_per_block
        self.wear_count = [0] * block_count
        self.free_blocks = set(range(block_count))
        self.controller = Controller(self, read_speed, write_speed)

    def write_data(self, data):
        self.controller.write(data)

    def read_data(self, page_address):
        return self.controller.read(page_address)

    def erase_block(self, block_index):
        for page in self.blocks[block_index].pages:
            for cell in page.cells:
                cell.state = 0
            page.valid_data = False
        self.blocks[block_index].erased = True
        self.wear_count[block_index] += 1
        self.free_blocks.add(block_index)

class Controller:
    def __init__(self, ssd, read_speed, write_speed):
        self.ssd = ssd
        self.current_block = 0
        self.current_page = 0
        self.valid_pages = []
        self.read_speed = read_speed
        self.write_speed = write_speed

    def write(self, data):
        if not data:
            return

        data_per_page = self.ssd.page_size
        pages_needed = (len(data) + data_per_page - 1) // data_per_page

        for _ in range(pages_needed):
            if self.current_page == self.ssd.pages_per_block:
                self.current_block = self.get_next_block()
                self.current_page = 0
                if self.current_block in self.ssd.free_blocks:
                    self.ssd.free_blocks.remove(self.current_block)
                else:
                    self.garbage_collect()

            page_data = data[:data_per_page]
            self.write_to_page(self.current_block, self.current_page, page_data)
            data = data[data_per_page:]
            self.current_page += 1
            time.sleep(len(page_data) / self.write_speed)

    def write_to_page(self, block_index, page_index, data):
        page = self.ssd.blocks[block_index].pages[page_index]
        corrected_data = self.error_correction(data)
        for i in range(len(corrected_data)):
            page.cells[i].state = corrected_data[i]
        page.valid_data = True
        self.valid_pages.append((block_index, page_index))

    def read(self, page_address):
        block_index, page_index = page_address
        page = self.ssd.blocks[block_index].pages[page_index]
        if page.valid_data:
            time.sleep(len(page.cells) / self.read_speed)
            data = [cell.state for cell in page.cells]
            return self.error_detection(data)
        else:
            return None

    def get_next_block(self):
        least_worn_blocks = [i for i, count in enumerate(self.ssd.wear_count) if count == min(self.ssd.wear_count)]
        return random.choice(least_worn_blocks)

    def garbage_collect(self):
        invalid_pages = [page for page in self.valid_pages if not self.ssd.blocks[page[0]].pages[page[1]].valid_data]
        if not invalid_pages:
            return

        # Choose a block to erase
        block_to_erase = random.choice(invalid_pages)[0]
        self.ssd.erase_block(block_to_erase)
        self.valid_pages = [page for page in self.valid_pages if page[0] != block_to_erase]

    def error_correction(self, data):
        # Using a simple Hamming(7,4) code for demonstration
        def hamming_encode(data):
            d = list(data)
            p1 = d[0] ^ d[1] ^ d[3]
            p2 = d[0] ^ d[2] ^ d[3]
            p3 = d[1] ^ d[2] ^ d[3]
            return d + [p1, p2, p3]

        encoded_data = []
        for i in range(0, len(data), 4):
            encoded_data.extend(hamming_encode(data[i:i+4]))
        return encoded_data

    def error_detection(self, data):
        # Using a simple Hamming(7,4) code for demonstration
        def hamming_decode(encoded_data):
            d = list(encoded_data[:4])
            p = list(encoded_data[4:])
            p1 = d[0] ^ d[1] ^ d[3]
            p2 = d[0] ^ d[2] ^ d[3]
            p3 = d[1] ^ d[2] ^ d[3]
            error_pos = (p1 ^ p[0]) * 1 + (p2 ^ p[1]) * 2 + (p3 ^ p[2]) * 4
            if error_pos != 0:
                d[error_pos - 1] = 1 - d[error_pos - 1]
            return d

        decoded_data = []
        for i in range(0, len(data), 7):
            decoded_data.extend(hamming_decode(data[i:i+7]))
        return decoded_data

def simulate_ssd():
    block_count = 10
    page_size = 16  # cells per page
    pages_per_block = 4
    read_speed = 500  # cells per second
    write_speed = 200  # cells per second

    ssd = SSD(block_count, page_size, pages_per_block, read_speed, write_speed)

    data1 = [1] * 30  # writing 30 cells of data
    ssd.write_data(data1)

    read_data = ssd.read_data((0, 0))  # read first page of the first block
    print("Read Data from (0, 0):", read_data)

    data2 = [1] * 50  # writing more data
    ssd.write_data(data2)

    read_data = ssd.read_data((0, 2))  # read third page of the first block
    print("Read Data from (0, 2):", read_data)

simulate_ssd()

