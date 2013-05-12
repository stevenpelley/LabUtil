# transform a dict pdf to a cdf
# any key with a value in inf_keys should be considered infinite and
# omitted from cumulative values (but included in the denominator.  This
# means that the graph will never reach 1.0)
#
# returns cdf as a dict, where val = cdf[i], 0 <= val <= 1.0
# interpret as val*100 percent of the distribution are at or below i
def PDF2CDF(pdf, inf_keys):
  total_count = float(sum(pdf.values()))
  cdf = {}
  accum = 0.0
  for value in sorted(pdf.keys()):
    frequency = pdf[value]
    if value not in inf_keys:
      accum += frequency
      cdf[value] = accum / total_count
  return cdf
