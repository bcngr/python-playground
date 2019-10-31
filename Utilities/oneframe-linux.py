import argparse
import random
import socket
import struct

DEST_MAC_STUB = [0xaa, 0xbb, 0xcc, 0xdd, 0xee]

def parseMAC (val):
  sep = ""
  if val.count(":"):
    sep = ":"
  elif val.count("-"):
    sep = "-"

  return [int(x, 16) for x in val.split(sep)]


BANNER = """
This program will send arbitrary ethernet frames for testing purposes.

By default it will send a frame on eth1, using the interface MAC address
as the source, to one of 256 random destination MAC addresses.
"""

def coerceBool (val, default):
  val = val.lower()
  if val == "y" or val == "yes":
    return True
  elif val == "n" or val == "no":
    return False
  else:
    return default

def inputString (prompt, default):
  user = raw_input(prompt).strip()
  if not user:
    return default
  return user

def inputBool (prompt, default):
  val = coerceBool(raw_input(prompt).strip(), default)
  return val

def parseargs ():
  parser = argparse.ArgumentParser()
  parser.add_argument("--interface", dest="intf", default=None)
  parser.add_argument("--src", dest="src", default=None)
  parser.add_argument("--use-intf-src", dest="intf_src", action="store_true", default=None)
  parser.add_argument("--dst", dest="dst", default=None)
  return parser.parse_args()

def config ():
  copts = parseargs()

  opts = {}
  if copts.intf:
    opts["intf"] = copts.intf
  else:
    opts["intf"] = inputString("Interface to send from [eth1]: ", "eth1")

  if copts.intf_src:
    opts["src-mac"] = open("/sys/class/net/%s/address" % (opts["intf"]), "r").read().strip()
  elif copts.src:
    opts["src-mac"] = copts.src
  else:
    if not inputBool("Use %s MAC as source [y]: " % (opts["intf"]), True):
      opts["src-mac"] = inputString("  Source MAC (in hexadecimal form): ", None)
    else:
      opts["src-mac"] = open("/sys/class/net/%s/address" % (opts["intf"]), "r").read().strip()
  print "  Using %s as source MAC" % (opts["src-mac"])

  if copts.dst:
    opts["dst-mac"] = copts.dst
  else:
    if inputBool("Specify destination MAC [n]: ", False):
      opts["dst-mac"] = inputString("  Destination MAC (in hexadecimal form): ", None)

  return opts

def main ():
  print BANNER
  opts = config()
  send(opts)

def send (opts):
  src_parts = parseMAC(opts["src-mac"])
  if opts.has_key("dst-mac"):
    dst_parts = parseMAC(opts["dst-mac"])
  else:
    dst_parts = DEST_MAC_STUB + [random.randint(0, 255)]

  hdr = struct.pack(">6B6BH", *(dst_parts + src_parts + [0x820]))
  s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
  s.bind((opts["intf"], 0))

  s.send(hdr + "hello")


if __name__ == '__main__':
  main()