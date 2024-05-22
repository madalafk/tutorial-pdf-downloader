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
    self.data_per_page = self.ssd.page_size
    self.pages_needed = (len(self.ssd.data) + self.data_per_page - 1) // self.data_per_page  # Pre-calculate data per page and pages needed

  def write(self, data):
    if not data:
      return

    for _ in range(self.pages_needed):
      if self.current_page == self.ssd.pages_per_block:
        self.current_block = self.get_next_block()
        self.current_page = 0
        if self.current_block in self.ssd.free_blocks:
          self.ssd.free_blocks.remove(self.current_block)
        else:
          self.garbage_collect()

      page_data = data[:self.data_per_page]
      data = data[self.data_per_page:]

      corrected_data = self.error_correction(page_data)
      self.write_to_page(self.current_block, self.current_page, corrected_data)
      self.current_page += 1
      time.sleep(len(corrected_data) / self.write_speed)

  def write_to_page(self, block_index, page_index, corrected_data):
    page = self.ssd.blocks[block_index].pages[page_index]
    page.cells[:len(corrected_data)] = corrected_data  # Use slicing for efficiency
    page.valid_data = True
    self.valid_pages.append((block_index, page_index))

  def read(self, page_address):
    block_index, page_index = page_address
    page = self.ssd.blocks[block_index].pages[page_index]
    if page.valid_data:
      time.sleep(len(page.cells) / self.read_speed)
      data = [cell.state for cell in page.cells]
      return self.error_detection(data)

