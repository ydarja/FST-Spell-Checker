# FST spell checker
A probabilistic spell checker built on weighted finite state transducers.  
  
**Authors:** Darja Jepifanova ([@ydarja](https://github.com/ydarja)), Giulio Cusenza ([@GiulioCusenza](https://github.com/GiulioCusenza)).

## Example
```
Insert word: wark
Correction candidates for misspelt word "wark":

	1. war 0.002319288751449555
	2. walk 0.0020736132711249356
	3. bark 0.0018018018018018014
	4. mark 0.001679261125104953
	5. wary 0.0012499999999999996
	6. park 0.0008849557522123889
	7. warm 0.0008396305625524772
	8. dark 0.000710227272727273
	9. ward 0.000710227272727273
	10. wars 0.00038491147036181687
	11. warn 0.00033715441672285923
```
The output includes the conditional probability of the edit operations. For example, the probability that given "r" we substitute it with "l" is P(l | r) = 0.0020736132711249356. We can assume P(walk | wark) = P(l | r) and thus give "walk" as the second correction candidate.
