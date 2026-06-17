# Container With Most Water

**Category:** Two Pointers
**Difficulty:** medium

## Problem Statement

Given an array `height` where `height[i]` is the height of a vertical line at
position `i`, pick **two lines** that together with the x-axis form a container.
Return the **maximum amount of water** it can hold.

Area between lines `i` and `j` = `min(height[i], height[j]) * (j - i)` — width
times the **shorter** wall.

```
height = [1, 8, 6, 2, 5, 4, 8, 3, 7]   ->  49   # lines at i=1 (h=8), i=8 (h=7): min(8,7)*7
height = [1, 1]                        ->  1
```

## Real-World Analogy

Socho deewar pe alag-alag height ke planks lage hain aur tum unke beech paani
bharna chahte ho. Paani sirf **chhote wale plank** ki height tak hi ruk sakta hai
(zyada bhar do to overflow). Aur jitne door do planks honge, utna **chaudai
(width)** zyada.

Ab trick: do log sabse bahar wale planks pe khade hain (`l` leftmost, `r`
rightmost) — max width se shuruaat. Area chhote plank se limited hai. To sochо —
agar tum **lambe** wale plank ko andar khisko, to width to kam hogi hi, aur height
bhi chhote plank se hi capped rahegi — koi faayda nahi. Lekin agar **chhote** wale
plank ko andar khisko, to shaayad uske peeche koi lamba plank mile jo zyada paani
roke. Isiliye hamesha **chhota wala pointer move karo**.

## Approach

Pattern: **two pointers from opposite ends, greedy move the shorter wall**. Widest
container se start karo, fir har step pe chhoti deewar ko andar lao — kyunki sirf
usi se bada area milne ka chance hai.

```python
def max_area(height):
    l, r = 0, len(height) - 1
    best = 0
    while l < r:
        area = min(height[l], height[r]) * (r - l)
        best = max(best, area)
        if height[l] < height[r]:
            l += 1          # chhoti deewar -> andar lao, bade ki talaash
        else:
            r -= 1
    return best
```

> **Brute force** har pair ka area nikaalta = O(n²). Two-pointer **O(n)** me karta:
> har move ek pointer ko andar laata, kabhi peeche nahi jaata.

**Greedy kyun sahi hai?** Jab chhoti deewar move karte ho, tum sirf un containers
ko chhod rahe ho jinki width kam hai *aur* height bhi usi chhoti deewar se capped
— wo kabhi current se bada nahi ho sakte. To unhe skip karna safe hai.

## Complexity

- **Time:** O(n) — `l` aur `r` mil kar pure array ko ek baar traverse karte hain.
- **Space:** O(1) — sirf pointers aur ek `best` variable.

## Common Pitfalls

- **Lamba wala pointer move karna** — galat. Hamesha **shorter** wall move karo,
  warna bada area miss ho jaayega.
- **Equal height pe confusion** — `height[l] == height[r]` ho to koi bhi move karo,
  result same rehta. Code me `<` se default `r -= 1` ho jaata, theek hai.
- **Area formula ulta** — width `(r - l)` hai aur height `min(...)`; `max` use mat
  karna height me, paani chhoti deewar pe rukta hai.
- **Sort karne ki galti** — yeh **trapping rain water** nahi hai; yahaan indices
  ki position (width) matter karti, sort karoge to width meaning kho jaayega.

## When to Use This Pattern

Jab "do positions choose karo jo kisi **width × height** type quantity ko maximize
kare" aur ek dimension ends pe widest ho → **opposite-end two pointers + greedy
shrink the limiting side**. Cue: "maximize area / max pair value, no need to sort."

## NeetCode Link

https://neetcode.io/problems/max-water-container
