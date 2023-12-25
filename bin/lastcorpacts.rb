#!/usr/bin/env ruby

require 'optparse'

Split = Struct.new(:symbol, :date, :split_factor) do
	def toString
		"#{symbol};#{date};#{split_factor}"
	end
end

if __FILE__ == $0
	begin
		corpActsTabFile = ""
	    OptionParser.new do |opts|
	    	opts.on("-f FILEPATH", "--filepath FILEPATH", "Path to CorpActs.tab file") do |v|
	    		corpActsTabFile = v
	    	end
	    end.parse!

	    lastSplits = Hash.new
	    currentDate = "19000101"
	    skippedMode = true
	    lineNumber = 0
		File.open(corpActsTabFile).each do |line|
			lineNumber = lineNumber + 1
			line = line.strip
			if !line
				next
			end

			if /^[12][0-9]{3}(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[01])$/.match?(line)
				if currentDate < line
					currentDate = line
					skippedMode = false
				else
					STDERR.puts "Unable to switch currentDate=" + currentDate + " to new=" + line + ". Enabled skipped mode"
					skippedMode = true
				end
				next
			end

			if skippedMode
				STDERR.puts "Skipped line " + lineNumber.to_s + ":'" + line + "'"
				next
			end

			m = /^(.*):(.*),(.*)/.match(line)
			if !m
				STDERR.puts "Unable to parse line " + lineNumber.to_s + ":'" + line + "'. Skipped"
				next
			end

			symbol = m[2].strip
			factor = m[3].strip

			if !symbol
				STDERR.puts "Skipped line " + lineNumber.to_s + ":'" + line + "' due empty symbol"
				next
			end

			item = Split.new(symbol, currentDate, factor)
			lastSplits[symbol] = item;
		end

		puts "symbol;split-date;split-factor"
		lastSplits.each{ |key, value| puts value.toString }
    rescue SystemExit => e
        raise e
    rescue Exception => e
        abort("expchains failed with error: #{e.message}, #{e.backtrace.inspect}")	
    end
end
