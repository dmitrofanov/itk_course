from random import randint
arr = [x + randint(1, 100) for x in range(100)]
arr.sort()
print(arr[:20])

def search(arr: list[int], number: int):
	iterations = 0
	lo, hi = 0, len(arr) - 1
	mid = (lo + hi) // 2
	while arr[mid] != number and lo < hi and iterations < 1000:
		if arr[mid] < number:
			lo, hi = mid + 1, hi
			mid = (lo + hi) // 2
		else:
			lo, hi = lo, mid - 1
			mid = (lo + hi) // 2
		print(lo, hi, mid)
		iterations += 1
	return arr[mid] == number

print(search(arr, 20))
