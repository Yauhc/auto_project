# -*- coding: utf-8 -*-
import sys
import io

# Set the default encoding for stdout to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Print a string with Chinese characters
print("你好，世界！")  # 输出中文

import sys
print(sys.executable)