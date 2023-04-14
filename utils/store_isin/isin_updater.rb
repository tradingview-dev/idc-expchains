#!/usr/bin/env ruby
require 'optparse'
require 'net/http'
require 'cgi'
require 'date'
require 'typhoeus'
require 'csv'
require 'json'

class ISINDownloader
    def initialize(options = {})
        @verbose = options[:verbose] || false
    end

    def getFeeds(urlPrefix, prodFilter)
        uri = URI("#{urlPrefix}/meta/info.json")
        if @verbose
            puts "#{uri}"
        end
        resp = Net::HTTP.get(uri)
        metainfo = JSON.parse(resp)

        feeds = []
        metainfo["upstreams"].each do |n, upstream|
            if upstream["provides_realtime"] && upstream["name"] =~ /rts/ && !(upstream["name"] =~ /test/)
                feeds << upstream["name"]
            end
        end

#        if prodFilter
#            feeds.select! {|f| f =~ /-sf-/}
#        end

        return feeds
    end


    def getSources(urlPrefix, feed)
        uri = URI("#{urlPrefix}/upstream/#{feed}/streaming/sources?useCodes=true")
        if @verbose
            puts "#{uri}"
        end
        resp = Net::HTTP.get(uri)
        sources = resp.split(/\n/)
        sources.select! {|s| !(s =~ /^922$/)}

#        sources.select! {|s| s =~ /^2500$/}
        return sources
    end

    def filterSymbols(feed, source, symbols)
        symbols.select! {|s| !(s =~ /^O[0-9]?:.*$/)}
        symbols.select! {|s| !(s =~ /^S[0-9]?:.*$/)}
#        symbols.select! {|s| !(s =~ /^B[0-9]?:.*$/)}
#        symbols.select! {|s| !(s =~ /^P[0-9]?:.*$/)}
#        symbols.select! {|s| !(s =~ /^W[0-9]?:.*$/)}
        symbols.select! {|s| !(s =~ /^F[0-9]?:.*$/)}
        return symbols
    end

    def getSymbolsParallel(urlPrefix, feed, sources)
        hydra = Typhoeus::Hydra.new(:max_concurrency => 100)

        requests = Hash.new
        sources.each do |source|
            uri = URI("#{urlPrefix}/upstream/#{feed}/streaming/symbols?sources=#{source}")
            if @verbose
                puts "#{uri}"
            end
            r = Typhoeus::Request.new(uri,
                followlocation: true,
                method: :get)
            requests[source] = r
            hydra.queue(r)
        end
        hydra.run

        sourceSymbols = {}

        requests.each do |source, request|
        begin
            next if request.response.code != 200
            symbols = request.response.body.split(/\n/)
            symbols = filterSymbols(feed, source, symbols)
            if !symbols.empty?
                sourceSymbols[source] = symbols
            else
                puts "Empty symbols for #{feed}/#{source}"
            end
        rescue
        end
        end

        return sourceSymbols
    end

    def filterDuplicatingSources(feedSymbols)
        filteredFeedSymbols = {}
        processedSources = []
        feedSymbols.each do |feed, sourceSymbols|
            filteredSourceSymbols = {}
            sourceSymbols.each do |source, symbols|
                if !processedSources.include?(source)
                    filteredSourceSymbols[source] = symbols
                    processedSources << source
                else
                    puts "Duplicating source #{feed}/#{source}"
                end
            end
            if !filteredSourceSymbols.empty?
                filteredFeedSymbols[feed] = filteredSourceSymbols
            end
        end

        return filteredFeedSymbols
    end

    def getAllSnapshotParallel(urlPrefix, feedSymbols)
        sourceSymbolsData = {}
        symbolList = []
        feedSymbols.each do |feed, sourceSymbols|
            sourceSymbols.each do |source, symbols|
                symbols.each do |symbol|
                    symbolList << [feed, source, symbol]
                end
            end
        end
        symbolList.shuffle!
        puts "Need to process #{symbolList.size} symbols"
        totalSymbols = symbolList.size
        processedSymbols = 0

        while !symbolList.empty? do
            symbols = symbolList.pop(500)
            hydra = Typhoeus::Hydra.new(:max_concurrency => 50)
            currentChunkSymbols = symbols.size

            requests = Hash.new
            symbols.each do |s|
                feed, source, symbol = s
                urlSymbol = CGI::escape(symbol).gsub(/\+/, "%2B")
                uri = URI("#{urlPrefix}/upstream/#{feed}/streaming/snapshot?source=#{source}&symbol=#{urlSymbol}")
                if @verbose
                    puts "#{uri}"
                end
                r = Typhoeus::Request.new(uri,
                    followlocation: true,
                    method: :get)
                requests[s] = r
                hydra.queue(r)
            end
            hydra.run

            requests.each do |s, request|
            begin
                feed, source, symbol = s
                if request.response.code != 200
                    puts "ERR #{request.response.code} on #{request.url}"
                    next
                end
                snapshot = JSON.parse(request.response.body)
                data = {}
                if snapshot["ISIN"]
                    data["isin"] = snapshot["ISIN"]
                end

                if !data.empty?
                    if sourceSymbolsData[source].nil?
                        sourceSymbolsData[source] = {}
                    end
                    sourceSymbolsData[source][symbol] = data
                else
                     puts "No isin for #{feed}/#{source}/#{symbol}"
                end
            rescue
            end
            end
            processedSymbols += currentChunkSymbols
            puts "Processed #{processedSymbols} of #{totalSymbols} (#{(((processedSymbols*1.0)/totalSymbols)*100).round(2)}%)"
        end

        return sourceSymbolsData
    end

    def getAllISIN(urlPrefix, feedSymbols)
        sourceData = getAllSnapshotParallel(urlPrefix, feedSymbols)
        return sourceData
    end

    def usIsin?(v)
        return v.start_with?("US") || v.start_with?("CA")
    end

    def mergeWriteISINData(dataPath, source, data, merge)
        filePath = "#{dataPath}/#{source}.csv"
        if !merge.nil?
            originalData = readISINData(dataPath, source)
            if merge == :overwrite
                puts "Merge-overwrite for existing file #{filePath}"
                data = originalData.merge(data) do |key, oldval, newval|
                    if oldval.nil?
                        newval
                    else
                        mergeval = oldval.merge(newval) do |k, o, n|
                            if !n.nil? && !n.empty? && !usIsin?(o)
                                n
                            else
                                o
                            end
                        end
                        mergeval
                    end
                end
            elsif merge == :append
                puts "Merge-append for existing file #{filePath}"
                data = originalData.merge(data) do |key, oldval, newval|
                    if oldval.nil?
                        newval
                    else
                        mergeval = oldval.merge(newval) do |k, o, n|
                            if !n.nil? && !n.empty? && usIsin?(n)
                                n
                            elsif !o.nil? && !o.empty?
                                o
                            else
                                n
                            end
                        end
                        mergeval
                    end
                end
            end
        else
            puts "Overwrite if file exists #{filePath}"
        end

        writeISINData(dataPath, source, data)
    end

    def mergeISINData(originalPath, newPath, targetPath, source, merge)
        data = readISINData(newPath, source)

        if !merge.nil?
            originalData = readISINData(originalPath, source)
            if merge == :overwrite
                data = originalData.merge(data) do |key, oldval, newval|
                    if oldval.nil?
                        newval
                    else
                        mergeval = oldval.merge(newval) do |k, o, n|
                            if !n.nil? && !n.empty? && !usIsin?(o)
                                n
                            else
                                o
                            end
                        end
                        mergeval
                    end
                end
            elsif merge == :append
                data = originalData.merge(data) do |key, oldval, newval|
                    if oldval.nil?
                        newval
                    else
                        mergeval = oldval.merge(newval) do |k, o, n|
                            if !n.nil? && !n.empty? && usIsin?(n)
                                n
                            elsif !o.nil? && !o.empty?
                                o
                            else
                                n
                            end
                        end
                        mergeval
                    end
                end
            end
        end

        writeISINData(targetPath, source, data)
    end

    def writeISINData(dataPath, source, data)
        filePath = "#{dataPath}/#{source}.csv"
        puts "Writing #{filePath}"

        CSV.open(filePath, "w") do |csv|
            csv << ["rts-ticker", "isin"]
            data.keys.sort.each do |s|
                d = data[s]
                if !d["isin"].nil? && !d["isin"].empty?
                    csv << [s, d["isin"]]
                end
            end
        end
    end

    def readISINData(dataPath, source)
        isinData = {}
        filePath = "#{dataPath}/#{source}.csv"
        puts "Loading #{filePath}"
        if !File.file? filePath
            return isinData
        end
        rawData = CSV.read(filePath)
        rawData.drop(1).each do |line|
            ticker, isin = line
            isinData[ticker] = {"isin" => isin}
        end

        return isinData
    end


    def run(options)
        urlPrefix = options[:urlPrefix] || 'http://idc-staging.trading+view.com:8071'
        dataPath = options[:dataPath] || "./"
        merge = options[:merge]
        prodFilter = options[:prodFilter]

        feeds = getFeeds(urlPrefix, prodFilter)

        feedSources = {}
        feeds.each do |feed|
            sources = getSources(urlPrefix, feed)
            feedSources[feed] = sources
        end

        feedSymbols = {}

        feedSources.each do |feed, sources|
            feedSymbols[feed] = getSymbolsParallel(urlPrefix, feed, sources)
        end
        feedSymbols = filterDuplicatingSources(feedSymbols)

        isinData = getAllISIN(urlPrefix, feedSymbols)

        isinData.each do |source, data|
            puts "Write isin for #{source}"
            mergeWriteISINData(dataPath, source, data, merge)
        end

        #pp isinData

        #feedSources.each {|f, s| s.each{|i| puts i}}
        # pp feedSymbols
    end

    def download(options)
        urlPrefix = options[:urlPrefix] || 'http://idc-staging.trading+view.com:8071'
        targetPath = options[:targetPath] || "./"
        prodFilter = options[:prodFilter]

        feeds = getFeeds(urlPrefix, prodFilter)

        feedSources = {}
        feeds.each do |feed|
            sources = getSources(urlPrefix, feed)
            feedSources[feed] = sources
        end

        feedSymbols = {}

        feedSources.each do |feed, sources|
            feedSymbols[feed] = getSymbolsParallel(urlPrefix, feed, sources)
        end
        feedSymbols = filterDuplicatingSources(feedSymbols)

        isinData = getAllISIN(urlPrefix, feedSymbols)

        puts "Writing to #{targetPath}"
        isinData.each do |source, data|
            puts "Write isin for #{source}"
            writeISINData(targetPath, source, data)
        end

        #pp isinData

        #feedSources.each {|f, s| s.each{|i| puts i}}
        # pp feedSymbols
    end

    def merge(options)
        urlPrefix = options[:urlPrefix] || 'http://idc-staging.trading+view.com:8071'
        prevPath = options[:prevPath] || "./"
        newPath = options[:newPath] || "./"
        targetPath = options[:targetPath] || "./"
        merge = options[:merge]


        Dir.glob("#{newPath}/*.csv").each do |f|
            source = File.basename( f, ".csv" )
            puts "Processing #{source}.csv"
            mergeISINData(prevPath, newPath, targetPath, source, merge)
        end
    end

end


if __FILE__ == $0
    options = {
    }

    global = OptionParser.new do |opts|
        opts.banner = "Usage: isin_updater.rb [options] [subcommand [options]]"
        opts.on("-v", "--[no-]verbose", "Run verbosely") do |v|
            options[:verbose] = v
        end
    end

    subcommands = {
        'download' => OptionParser.new do |opts|
            opts.banner = "Usage: download [options]"
            opts.on("-U PREFIX", "--url-prefix PREFIX") do |v|
                options[:urlPrefix] = v
            end
            opts.on("-D PATH", "--data path") do |v|
                options[:targetPath] = v
            end
        end,
        'merge' => OptionParser.new do |opts|
            opts.banner = "Usage: merge [options]"

            opts.on("--prev-data path") do |v|
                options[:prevPath] = v
            end
            opts.on("--new-data path") do |v|
                options[:newPath] = v
            end
            opts.on("--target-data path") do |v|
                options[:targetPath] = v
            end

            opts.on("-A", "--append") do |v|
                options[:merge] = :append
            end
            opts.on("-O", "--overwrite") do |v|
                options[:merge] = :overwrite
            end
        end
    }

    global.order!
    command = ARGV.shift
    subcommands[command].order!

    requester = ISINDownloader.new(options)
    puts "Command: #{command} "
    case command
    when "download"
        requester.download(options)
    when "merge"
        requester.merge(options)
    else
        puts "Unsupported command"
        exit(1)
    end
end