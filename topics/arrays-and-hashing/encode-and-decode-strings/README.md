# Encode and Decode Strings

**Category:** Arrays & Hashing
**Difficulty:** medium

## Problem Statement

Design two functions: `encode(strs)` turns a list of strings into a **single string**, and `decode(s)` turns that single string back into the **original list**. The catch: the strings can contain **any** character — including the one you'd love to use as a separator. So you can't just `"#".join(strs)`, because a string itself might contain `#`.

```
encode(["neet", "code", "love", "you"])  ->  "4#neet4#code4#love3#you"
decode("4#neet4#code4#love3#you")        ->  ["neet", "code", "love", "you"]
```

## Real-World Analogy

Socho tum courier company chalate ho aur ek bade box me kaई parcels bhej rahe ho. Agar tum parcels ke beech sirf tape lagao (separator) to problem — kisi parcel ke andar bhi waisi hi tape ho sakti hai, receiver confuse ho jayega kahan ek parcel khatam hua. Smart tareeka: **har parcel se pehle ek label chipka do jo batata hai "agla parcel exactly 4 kg ka hai"**. Receiver label padhta hai, exactly utna weight ginta hai, agla parcel nikaal leta hai — chahe parcel ke andar kuch bhi ho, weight kabhi jhooth nahi bolta. Yeh **length-prefix encoding** hai: har string se pehle uski **length + ek delimiter** likho. Length se exactly pata chal jaata hai kitne characters padhne hain, isliye string ke andar `#` aaye ya kuch bhi — koi farak nahi padta.

## Approach

Naive idea — `"#".join(strs)` — fails kyunki koi string khud `#` rakh sakti hai, decode confuse ho jaayega. Solution: **length-prefixing**.

**Encode:** har string `s` ke liye likho `len(s)` + `"#"` + `s`. `#` sirf length ko string se alag karta hai; length self ko decode karne ke liye use hoti hai, `#` ko nahi.

**Decode:** pointer `i` se chalo. Pehle digits padho jab tak `#` na mile — yeh length hai. `#` ke turant baad se exactly utne characters slice karo (chahe unme `#` ho). Phir pointer ko aage le jao aur repeat.

```python
def encode(strs):
    return "".join(f"{len(s)}#{s}" for s in strs)

def decode(s):
    res, i = [], 0
    while i < len(s):
        j = i
        while s[j] != '#':         # read the length digits
            j += 1
        length = int(s[i:j])
        word = s[j + 1 : j + 1 + length]   # exactly `length` chars
        res.append(word)
        i = j + 1 + length          # jump past this chunk
    return res
```

Pattern: **length-prefixed (self-delimiting) encoding** — same idea jo TCP/protobuf jaise wire protocols me hota hai.

## Complexity

Maan lo total characters across all strings = `N`.

- **Time:** O(N) for both encode and decode — har character ko constant baar touch karte hain. (Length digits chhote hote hain, ignore kar sakte ho.)
- **Space:** O(N) for the output (encoded string ya decoded list). Extra working space O(1) beyond output.

## Common Pitfalls

- **Plain delimiter (`#`, `,`, space) join** — fail jab string khud wahi character rakhti ho. Length-prefix isi se bachata hai.
- **Multi-digit lengths galat padhna** — length `12` do digits ka hai. Isliye `#` tak **saare** digits padho, sirf ek character nahi.
- **`#` ko string ka part samajhna** — `#` length aur content ke beech ka separator hai; content slice length ke hisaab se hota hai, agle `#` tak nahi.
- **Empty strings** — `""` ko `"0#"` encode karo. Decode me length `0`, empty word append hota hai — handle karna mat bhoolo.
- **Pointer arithmetic off-by-one** — content `j+1` se shuru hota hai (`#` ke baad), aur next chunk `j + 1 + length` pe.

## When to Use This Pattern

Jab tumhe **arbitrary data ko ek flat stream/string me serialize** karna ho aur content me koi bhi byte aa sakti ho — socho **length-prefixing**. Yeh wahi technique hai jo network protocols, file formats, aur message framing me use hoti hai: "pehle batao kitna data aa raha hai, phir utna data bhejo." Delimiter-escaping ke jhanjhat se bachne ka clean tareeka.

## Visual

Open [visual.html](visual.html) in your browser for an interactive step-by-step walkthrough of length-prefixed encoding and decoding.

## NeetCode Link

https://neetcode.io/problems/string-encode-and-decode
