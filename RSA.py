from sys import exit
from random import randint
from math import gcd
from time import sleep


class Helper:
	@classmethod
	def is_prime(cls, n: int) -> bool:
		"""
		Determine if integer n is prime
		:param n: integer to check
		:return: True if n is prime, False otherwise
		"""
		if n in [2, 3]:
			return True
		if n <= 1 or n % 2 == 0:
			return False

		r: int = 0
		s: int = n - 1

		while s % 2 == 0:
			r += 1
			s //= 2

		for _ in range(10):
			a: int = randint(2, n - 1)
			x: int = pow(a, s, n)
			if x in [1, n - 1]:
				continue
			for _ in range(r - 1):
				x = pow(x, 2, n)
				if x == n - 1:
					break
			else:
				return False
		return True

	@classmethod
	def gen_prime(cls, lng: int) -> int:
		"""
		Generate a random prime number of length lng
		:param lng: Length of the prime to generate
		:return: A random prime number of length lng
		"""
		while True:
			p: int = randint(10 ** (lng - 1), 10 ** lng)
			if cls.is_prime(p):
				return p


class Person:
	def __init__(self, name: str, keylen: int = None) -> None:
		self.name: str = name
		self.pubkey: tuple[int, int]
		self.__prvkey: tuple[int, int]
		if keylen:
			self.pubkey, self.__prvkey = Person.gen_keys(keylen)
		else:
			self.pubkey, self.__prvkey = Person.gen_keys(4)

	def __repr__(self) -> str:
		return f"{self.name}  {self.pubkey}"

	def __encrypt(self, to, m: int) -> int:
		"""
		Encrypt a single character by Unicode value
		:param to: Recipient of the message
		:param m: Unicode value of character to encrypt
		:return: Unicode value of encrypted ciphertext character
		"""
		e: int
		n: int
		e, n = to.pubkey
		return pow(m, e, n)

	def __decrypt(self, c: int) -> int:
		"""
		Decrypt a single character by Unicode value
		:param c: Unicode value of character to decrypt
		:return: Unicode value of decrypted plaintext character
		"""
		d: int
		n: int
		d, n = self.__prvkey
		return pow(c, d, n)

	def encrypt_message(self, to, m: str) -> str:
		"""
		Encrypt a message
		:param to: Recipient of the message
		:param m: Plaintext message
		:return: Encrypted ciphertext message
		"""
		c: str = ""
		for char in m:
			c += chr(self.__encrypt(to, ord(char)))
		return c

	def decrypt_message(self, c: str) -> str:
		"""
		Decrypt a message
		:param c: Ciphertext message
		:return: Decrypted plaintext message
		"""
		m: str = ""
		for char in c:
			m += chr(self.__decrypt(ord(char)))
		return m

	def compare_found_key(self, d: int) -> bool:
		"""
		Check that a key found by brute force is the same as private key d
		:param d: Found key
		:return: True if the found key matches the private key, False otherwise
		"""
		return d == self.__prvkey[0]

	@classmethod
	def gen_keys(cls, lng: int, showkeys: bool = False) -> tuple[tuple[int, int], tuple[int, int]]:
		"""
		Generate a pair of RSA keys
		:param lng: Length of the prime numbers to use in key generation
		:param showkeys: True to print key generation data, False otherwise
		:return: Tuple of RSA keys (e, n), (d, n)
		"""
		p: int = Helper.gen_prime(lng)
		q: int = Helper.gen_prime(lng)

		n: int = p * q
		r: int = (p - 1) * (q - 1)

		e: int = randint(2, r - 1)
		while gcd(e, r) != 1:
			e = randint(2, r - 1)

		d: int = pow(e, -1, r)

		if showkeys:
			print(f"p = {p}")
			print(f"q = {q}")
			sleep(PAUSE)
			print(f"n = p * q = {n}")
			print(f"r = (p - 1)(q - 1) = {r}")
			sleep(PAUSE)
			print(f"e = random coprime to r = {e}")
			print(f"d = e^-1 mod r = {d}")
			sleep(PAUSE)
			print(f"keys (e, n), d = ({e}, {n}), {d}")

		return (e, n), (d, n)


class Hacker(Person):
	def __init__(self, name: str, keylen: int = None) -> None:
		super().__init__(name, keylen)

	def __bf_decrypt(self, c: int, key: tuple[int, int]) -> int:
		"""
		Decrypt a single character during brute force attack
		:param c: Unicode value of ciphertext character
		:param key: Key being attempted
		:return: Unicode value of decrypted character
		"""
		d: int
		n: int
		d, n = key
		return pow(c, d, n)

	def __bf_decrypt_message(self, c: str, key: tuple[int, int]) -> str:
		"""
		Decrypt a message during a brute force attack
		:param c: Ciphertext message
		:param key: Key being attempted
		:return: Attempted decrypted string
		"""
		m: str = ""
		for char in c:
			m += chr(self.__bf_decrypt(ord(char), key))
		return m

	def frequency_analysis(self) -> dict[str, int]:
		"""
		Count the occurrences of each character in a ciphertext
		:return: Dictionary of count of character occurrences
		"""
		fa: dict[str, int] = {}
		for char in Main.c:
			if char in fa:
				fa[char] += 1
			else:
				fa[char] = 1
		return fa

	def brute_force(self, to: Person) -> None:
		"""
		Attempt to decrypt a message using brute force
		:param to: Intended recipient of the message
		:return: None
		"""
		n: int = to.pubkey[1]  # Get n from the sender's public key
		print(f"n = {n}")
		print("Beginning brute force...")
		for d in range(n):
			tempm: str = self.__bf_decrypt_message(Main.c, (d, n))
			print(tempm)
			if tempm == Main.m:
				print(f"Found valid key d = {d}")
				return


class Main:
	# Declare m and c as static properties
	m: str = ""
	c: str = ""

	global alice, bob, charlie

	@classmethod
	def menu(cls) -> None:
		print("\n======================================")
		print("1. Generate keys")
		print("2. Show current plaintext and ciphertext")
		print("3. Alice encrypts message")
		print("4. Bob decrypts message")
		print("5. Charlie starts frequency analysis")
		print("6. Charlie does brute force")
		print("0. End program")
		try:
			choice: int = int(input("Enter choice > "))
			match choice:
				case 1:
					cls.show_key_generation()
				case 2:
					cls.show_current_texts()
				case 3:
					cls.alice_encrypts()
				case 4:
					cls.bob_decrypts()
				case 5:
					cls.charlie_fa()
				case 6:
					cls.charlie_brute_force()
				case 0:
					exit(1502)
				case _:  # Default
					print("Not a valid option")
			sleep(PAUSE)  # Leave a bit of time to read the screen before showing the next thing
		except TypeError:
			print("Not a valid option")
		except ValueError:
			print("Not a valid option")

	@classmethod
	def show_key_generation(cls) -> None:
		lng: int = int(input("Enter prime length (<= 5) > "))
		if lng >= 6:
			print("Invalid prime length")
			return
		Person.gen_keys(lng, True)

	@classmethod
	def show_current_texts(cls) -> None:
		print(f"Current plaintext m: {Main.m}")
		print(f"Current ciphertext c: {Main.c}")

	@classmethod
	def alice_encrypts(cls) -> None:
		Main.m = input("You are Alice. What are you sending Bob? > ")
		print("For every character m, send m^eb mod nb")

		Main.c = alice.encrypt_message(bob, Main.m)
		print(f"Bob receives:\n{Main.c}")

	@classmethod
	def bob_decrypts(cls) -> None:
		print(f"Bob receives:\n{Main.c}")
		print("For every character c, decrypt c^db mod nb")
		print(f"Bob decrypts: \"{bob.decrypt_message(Main.c)}\"")

	@classmethod
	def charlie_fa(cls) -> None:
		print("Charlie counts:")
		print(charlie.frequency_analysis())

	@classmethod
	def charlie_brute_force(cls) -> None:
		charlie.brute_force(bob)


# Meet Alice and Bob!
alice: Person = Person("Alice", 2)
bob: Person = Person("Bob", 2)
# And Charlie
charlie: Hacker = Hacker("Charlie", 2)

PAUSE: float = 0.9
while True:
	Main.menu()
