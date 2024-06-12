import os
import hashlib  # PBKDF2算法根据口令生成密钥
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad  # 使用标准PKCS#7填充法，进行边界填充与移除填充。

root_dir = os.path.dirname(__file__)
encrypted_dir = os.path.join(root_dir, 'encrypted_config_files')
# 明文文件，密文文件
file_groups = [
    ['ingestion-service/.env.example', 'ingestion-service.env.example'],  # 检索服务配置
    ['inference-service/backend/.env.example', 'inference-service.backend.env.example'],  # 推理服务后端配置
    ['inference-service/frontend/.env', 'inference-service.frontend.env'],  # 推理服务前端配置
]


def do_encrypt():
    """
    加密程序，将明文文件，加密为密文文件
    """
    # password = getpass.getpass("请输入密码：")
    password = input("请输入密码（调试用）：")  # 调试用
    for group in file_groups:
        plain_file = os.path.join(root_dir, group[0])
        encrypted_file = os.path.join(encrypted_dir, group[1])
        _cipher(True, plain_file, encrypted_file, password)
        print(plain_file + '--->' + encrypted_file)
    print('加密完成')


def do_decrypt():
    """
    加密程序，将密文文件，解密为明文文件
    """
    # password = getpass.getpass("请输入密码：")
    password = input("请输入密码（调试用）：")  # 调试用
    for group in file_groups:
        plain_file = os.path.join(root_dir, group[0])
        encrypted_file = os.path.join(encrypted_dir, group[1])
        _cipher(False, plain_file, encrypted_file, password)
        print(plain_file + '<---' + encrypted_file)
    print('解密完成')


def _cipher(do_encrypt:bool, plain_file:str, encrypted_file:str, password:str):
    """
    执行加密操作。
    param: do_encrypt true执行加密，false执行解密。
    in_file: 输入文件的绝对路径
    out_file: 输出文件的绝对路径
    """
    pbkdf_salt = "12345678"
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), pbkdf_salt.encode('utf-8'), 100000, 16)  # 生成128位密钥
    chunk_size = 16  # 每次读取的块大小
    # 加密
    if do_encrypt:
        encryptor = AES.new(key, AES.MODE_ECB)  # 使用ECB模式创建AES加密器
        with open(plain_file, 'rb') as f_in, open(encrypted_file, 'wb') as f_out:
            while True:
                chunk = f_in.read(chunk_size)
                if len(chunk) == 0:
                    break
                elif len(chunk) % chunk_size != 0:
                    # 最后一个块大小不是16的倍数时，需要进行填充
                    chunk = pad(chunk, chunk_size)
                encrypted_chunk = encryptor.encrypt(chunk)
                f_out.write(encrypted_chunk)
    # 解密
    else:
        decryptor = AES.new(key, AES.MODE_ECB)  # 使用ECB模式创建AES解密器
        with open(encrypted_file, 'rb') as f_in, open(plain_file, 'wb') as f_out:
            while True:
                chunk = f_in.read(chunk_size)
                if len(chunk) == 0:
                    break
                decrypted_chunk = decryptor.decrypt(chunk)
                try:
                    # 如果并没有进行填充，会抛出一个异常，此时我们使用原始数据即可
                    unpadded_chunk = unpad(decrypted_chunk, chunk_size)
                except Exception as e:
                    unpadded_chunk = decrypted_chunk
                f_out.write(unpadded_chunk)


# 生成 requirements.txt: `$ pipreqs .`

if __name__ == '__main__':
    # do_encrypt()
    do_decrypt()
