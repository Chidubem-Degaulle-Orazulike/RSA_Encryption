from tkinter import *
from random import randint, choice
from math import gcd


class RSAButton(Button):
	def __init__(self, *args, **kwargs) -> None:
		super().__init__(bg="#dee0ff", relief="raised", borderwidth=3, *args, **kwargs)


class Helper:
	@classmethod
	def is_prime(cls, n: int) -> bool:
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
		while True:
			p: int = randint(10 ** (lng - 1), 10 ** lng)
			if cls.is_prime(p):
				return p

	@classmethod
	def sort_dict(cls, dic: dict[str, int]) -> dict[str, int]:
		arr: list[tuple[str, int]] = []
		for key in dic:
			arr.append((key, dic[key]))

		swap: bool = True
		n: int = len(arr) - 1
		while swap:
			swap = False
			for i in range(0, n - 1, 1):
				if arr[i][1] < arr[i + 1][1]:
					arr[i], arr[i + 1] = arr[i + 1], arr[i]
					swap = True
			n -= 1
		return {item[0]: item[1] for item in arr}


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
		e: int
		n: int
		e, n = to.pubkey
		return pow(m, e, n)

	def __decrypt(self, c: int) -> int:
		d: int
		n: int
		d, n = self.__prvkey
		return pow(c, d, n)

	def encrypt_message(self, to, m: str) -> str:
		c: str = ""
		for char in m:
			c += chr(self.__encrypt(to, ord(char)))
		return c

	def decrypt_message(self, c: str) -> str:
		m: str = ""
		for char in c:
			m += chr(self.__decrypt(ord(char)))
		return m

	def compare_found_key(self, d: int) -> bool:
		return d == self.__prvkey[0]

	@classmethod
	def gen_keys(cls, lng: int, returnAll: bool = False) -> tuple[tuple[int, int], tuple[int, int]] or tuple[int]:
		p: int = Helper.gen_prime(lng)
		q: int = Helper.gen_prime(lng)

		n: int = p * q
		r: int = (p - 1) * (q - 1)

		e: int = randint(2, r - 1)
		while gcd(e, r) != 1:
			e = randint(2, r - 1)

		d: int = pow(e, -1, r)

		if returnAll:
			return p, q, n, r, e, d
		return (e, n), (d, n)


class Hacker(Person):
	def __init__(self, name: str, keylen: int = None) -> None:
		super().__init__(name, keylen)

	def __bf_decrypt(self, c: int, key: tuple[int, int]) -> int:
		d: int
		n: int
		d, n = key
		return pow(c, d, n)

	def __bf_decrypt_message(self, c: str, key: tuple[int, int]) -> str:
		m: str = ""
		for char in c:
			m += chr(self.__bf_decrypt(ord(char), key))
		return m

	def frequency_analysis(self) -> dict[str, int]:
		fa: dict[str, int] = {}
		for char in Main.c:
			if char in fa:
				fa[char] += 1
			else:
				fa[char] = 1
		return Helper.sort_dict(fa)

	def brute_force(self, to: Person) -> tuple[int or None, list[str], str or None]:
		n: int = to.pubkey[1]  # Get n from the sender's public key
		attempts: list[str] = []
		for d in range(n):
			try:
				tempm: str = self.__bf_decrypt_message(Main.c, (d, n))
			except UnicodeEncodeError:
				tempm = "Failed to decrypt!"

			if tempm == Main.m:
				return d, attempts, tempm
			elif tempm != "Failed to decrypt!":
				attempts.append(tempm)
		return None, attempts, None


class Main:
	m: str = ""
	c: str = ""

	m_tk: StringVar
	root: Tk

	@classmethod
	def main(cls) -> None:
		cls.root = Tk()
		cls.root.tk.call("tk", "scaling", 1.5)
		cls.root.title("RSA Encryption")
		cls.root.after(0, cls.menu)

		cls.m_tk = StringVar()

		cls.root.mainloop()

	@classmethod
	def __clearScreen(cls) -> None:
		# Clear the screen the lazy way, by removing every element on it
		[widget.destroy() for widget in cls.root.winfo_children()]

	@classmethod
	def menu(cls) -> None:
		cls.__clearScreen()
		Label(text="RSA Encryption").grid(row=0, column=0)
		RSAButton(cls.root, text="Demonstrate key generation", command=cls.__key_generation, width=45).grid(row=1, column=0)
		RSAButton(cls.root, text="Show current texts", command=cls.__show_current_texts, width=45).grid(row=2, column=0)
		RSAButton(cls.root, text="Encrypt message", command=cls.__alice_encrypts_input, width=45).grid(row=3, column=0)
		RSAButton(cls.root, text="Decrypt message", command=cls.__bob_decrypts, width=45).grid(row=4, column=0)
		RSAButton(cls.root, text="Charlie does frequency analysis", command=cls.__charlie_fa, width=45).grid(row=5, column=0)
		RSAButton(cls.root, text="Charlie does brute force", command=cls.__charlie_brute_force, width=45).grid(row=6, column=0)
		RSAButton(cls.root, text="Close program", command=cls.root.destroy, width=45).grid(row=7, column=0)

	@classmethod
	def __key_generation(cls) -> None:
		cls.__clearScreen()

		lng: int = randint(1, 5)
		keys: tuple[int] = Person.gen_keys(lng, True)

		Label(text=f"p = {keys[0]}").grid(row=0, column=0)
		Label(text=f"q = {keys[1]}").grid(row=1, column=0)
		Label(text=f"n = p * q = {keys[2]}").grid(row=2, column=0)
		Label(text=f"r = (p - 1)(q - 1) = {keys[3]}").grid(row=3, column=0)
		Label(text=f"e = random coprime to r in [2, r - 1] = {keys[4]}").grid(row=4, column=0)
		Label(text=f"d = e^-1 mod r = {keys[5]}").grid(row=5, column=0)

		if keys[4] == keys[5]:
			Label(text="e = d  :  Insecure keys!", bg="#ff4444").grid(row=6, column=0)

		Label(text=f"Public key = ({keys[4]}, {keys[2]})").grid(row=7, column=0)
		Label(text=f"Private key = ({keys[5]}, {keys[2]})").grid(row=8, column=0)
		RSAButton(cls.root, text="Back to Menu", command=cls.menu, width=45).grid(row=9, column=0)

	@classmethod
	def __show_current_texts(cls) -> None:
		cls.__clearScreen()

		Label(text="Current plaintext m:").grid(row=0, column=0)
		Label(text=cls.m).grid(row=1, column=0)
		Label(text="Current ciphertext c:").grid(row=2, column=0)
		Label(text=cls.c).grid(row=3, column=0)

		RSAButton(cls.root, text="Back to Menu", command=cls.menu, width=45).grid(row=4, column=0)

	@classmethod
	def __alice_encrypts_input(cls) -> None:
		cls.__clearScreen()

		Label(text="You are Alice. Enter a message to send to Bob:").grid(row=0, column=0)

		cls.m_tk.set("")
		entry: Entry = Entry(textvariable=cls.m_tk)
		entry.bind("<Return>", cls.__alice_encrypts)
		entry.grid(row=1, column=0)

		RSAButton(cls.root, text="Encrypt", command=cls.__alice_encrypts, width=45).grid(row=2, column=0)
		RSAButton(cls.root, text="Back to Menu", command=cls.menu, width=45).grid(row=3, column=0)
		entry.focus_set()

	@classmethod
	def __alice_encrypts(cls, event: Event = None) -> None:
		cls.__clearScreen()

		cls.m = cls.m_tk.get()

		Label(text="Plaintext:").grid(row=0, column=0)
		Label(text=cls.m).grid(row=1, column=0)

		cls.c = alice.encrypt_message(bob, cls.m)

		Label(text="Encrypted ciphertext:").grid(row=2, column=0)
		Label(text=cls.c).grid(row=3, column=0)

		RSAButton(cls.root, text="Back to Menu", command=cls.menu, width=45).grid(row=4, column=0)

	@classmethod
	def __bob_decrypts(cls) -> None:
		cls.__clearScreen()

		Label(text="Bob receives:").grid(row=0, column=0)
		Label(text=cls.c).grid(row=1, column=0)

		Label(text="Bob decrypts:").grid(row=2, column=0)
		Label(text=bob.decrypt_message(cls.c)).grid(row=3, column=0)

		RSAButton(cls.root, text="Back to Menu", command=cls.menu, width=45).grid(row=4, column=0)

	@classmethod
	def __charlie_fa(cls) -> None:
		cls.__clearScreen()
		print(charlie.frequency_analysis())
		fa_dict: dict[str, int] = charlie.frequency_analysis()
		i: int = 0
		for key in fa_dict:
			Label(text=f"{key} : {fa_dict[key]}").grid(row=i, column=0)
			i += 1
		RSAButton(cls.root, text="Back to Menu", command=cls.menu, width=45).grid(row=i + 1, column=0)

	@classmethod
	def __charlie_brute_force(cls) -> None:
		cls.__clearScreen()
		Label(text=f"Charlie knows n = {bob.pubkey[1]}").grid(row=0, column=0)
		Label(text="Charlie tries brute force to find a valid d").grid(row=1, column=0)

		found_d: int or None
		failed_attempts: list[str]
		found_m: str or None
		found_d, failed_attempts, found_m = charlie.brute_force(bob)

		if found_d and failed_attempts and found_m:
			Label(text=f"Found a valid d = {found_d}").grid(row=2, column=0)
			Label(text="Charlie learned the plaintext:").grid(row=3, column=0)
			Label(text=found_m).grid(row=4, column=0)
			Label(text="Some other decryptions Charlie tried:").grid(row=5, column=0)
			for i in range(6, 9, 1):
				if failed_attempts:
					item: str = choice(failed_attempts)
					failed_attempts.remove(item)
					Label(text=item).grid(row=i, column=0)
				else:
					break
		else:
			Label(text="Charlie's brute force failed").grid(row=2, column=0)
			Label(text="and could not find a likely plaintext").grid(row=3, column=0)

		RSAButton(cls.root, text="Back to Menu", command=cls.menu, width=45).grid(row=10, column=0)


alice: Person = Person("Alice", 3)
bob: Person = Person("Bob", 3)
charlie: Hacker = Hacker("Charlie", 3)

Main.main()
