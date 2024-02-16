#!/usr/bin/env ruby
require 'optparse'
require 'csv'
require 'json'

class CMCProperties
    def initialize(options = {})
        @file = options[:file]
        @currencies = options[:currencies]
        @outFile = options[:outFile]
    end

    def mapCurrencyId(currency)
        if "#{currency.upcase}" == "GRT"
            return "XTVCGRAPH"
        end
        return "XTVC#{currency.upcase}"
    end

    def readCurrencies(currenciesPath)
        data = JSON.parse(File.read(currenciesPath))
        result = {}
        data.each do |record|
            result[record["id"]] = record
        end
        return result
    end

    def run()
        data = JSON.parse(File.read(@file))["data"]
        defiCoins = data.select {|r| (r["tags"]||[]).include? "defi"}

        currencies = readCurrencies(@currencies)

        defiCoinsIds = []
        defiCoins.each do |record|
            id = mapCurrencyId(record["symbol"])
            if not currencies.key? id
                puts "WARN: Unknown currency-id #{id}"
            end
            defiCoinsIds << id
        end
        defiCoinsIds.sort!
        CSV.open(@outFile, "w") do |csv|
            csv << ["currency-id", "typespecs"]
            defiCoinsIds.each do |id|
                csv << [id, "+:defi"]
            end
        end
    end
end


if __FILE__ == $0

        options = {
        }

        OptionParser.new do |opts|
            opts.on("-f FILE", "--file FILE") do |v|
                options[:file] = v
            end
            opts.on("-c CURRENCIES", "--currencies CURRENCIES") do |v|
                options[:currencies] = v
            end
            opts.on("-o OUTPUT", "--output OUTPUT") do |v|
                options[:outFile] = v
            end

        end.parse!

        filename = ARGV[0]

        requester = CMCProperties.new(options)

        requester.run
end