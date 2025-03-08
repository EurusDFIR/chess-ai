#!/bin/bash
base_url="https://tablebase.sesse.net/syzygy/3-4-5/"
files=(
  "KBBBvK.rtbw" "KBBBvK.rtbz" "KBBNvK.rtbw" "KBBNvK.rtbz"
    "KBBPvK.rtbw" "KBBPvK.rtbz" "KBBvK.rtbw" "KBBvK.rtbz"
      "KBBvKB.rtbw" "KBBvKB.rtbz" "KBBvKN.rtbw" "KBBvKN.rtbz"
        "KBBvKP.rtbw" "KBBvKP.rtbz" "KBBvKQ.rtbw" "KBBvKQ.rtbz"
	  "KBBvKR.rtbw" "KBBvKR.rtbz" "KBNNvK.rtbw" "KBNNvK.rtbz"
	    "KBNPvK.rtbw" "KBNPvK.rtbz" "KBNvK.rtbw" "KBNvK.rtbz"
	      "KBNvKB.rtbw" "KBNvKB.rtbz" "KBNvKN.rtbw" "KBNvKN.rtbz"
	        "KBNvKP.rtbw" "KBNvKP.rtbz" "KBNvKQ.rtbw" "KBNvKQ.rtbz"
		  "KBNvKR.rtbw" "KBNvKR.rtbz" "KBPPvK.rtbw" "KBPPvK.rtbz"
		    "KBPvK.rtbw" "KBPvK.rtbz" "KBPvKB.rtbw" "KBPvKB.rtbz"
		      "KBPvKN.rtbw" "KBPvKN.rtbz" "KBPvKP.rtbw" "KBPvKP.rtbz"
		        "KBPvKQ.rtbw" "KBPvKQ.rtbz" "KBPvKR.rtbw" "KBPvKR.rtbz"
			  "KBvK.rtbw" "KBvK.rtbz" "KBvKB.rtbw" "KBvKB.rtbz"
			    "KBvKN.rtbw" "KBvKN.rtbz" "KBvKP.rtbw" "KBvKP.rtbz"
		    )

		    mkdir -p syzygy
		    cd syzygy

		    for file in "${files[@]}"; do
		      wget --no-check-certificate "${base_url}${file}"
		      done
